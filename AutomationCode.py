import csv
import asyncio
import logging
import secrets
import string
import config
from typing import Optional
from pydantic import BaseModel, Field, ValidationError, model_validator

# Azure & Microsoft Graph Imports
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.user import User
from msgraph.generated.models.password_profile import PasswordProfile
from msgraph.generated.models.reference_update import ReferenceUpdate

# --- 1. LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("execution_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- 2. PYDANTIC DATA SCHEMA ---
def _generate_temp_password(length: int = 16) -> str:
    """Generates a password meeting Entra ID's default complexity rules."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        candidate = "".join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in candidate) and any(c.isupper() for c in candidate)
                and any(c.isdigit() for c in candidate) and any(c in "!@#$%^&*" for c in candidate)):
            return candidate


class UserModel(BaseModel):
    display_name: str = Field(..., alias='displayName')
    given_name: str = Field(..., alias='givenName')
    surname: str = Field(..., alias='surname')
    user_principal_name: str = Field(..., alias='userPrincipalName')
    department: Optional[str] = Field(None, alias='department')
    job_title: Optional[str] = Field(None, alias='jobTitle')
    manager_upn: Optional[str] = Field(None, alias='managerUPN')
    usage_location: Optional[str] = Field(None, alias='usageLocation')
    mail_nickname: Optional[str] = Field(None, alias='mailNickname')
    password: Optional[str] = None

    class Config:
        populate_by_name = True

    @model_validator(mode='after')
    def fill_derived_fields(self):
        # users.csv has no mailNickname/password columns, so derive them here.
        if not self.mail_nickname:
            self.mail_nickname = self.user_principal_name.split('@')[0]
        if self.manager_upn:
            self.manager_upn = self.manager_upn.strip() or None
        if not self.password:
            self.password = _generate_temp_password()
        return self

# --- AUTHENTICATION ---
credential = ClientSecretCredential(
    tenant_id=config.TENANT_ID,
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET
)
client = GraphServiceClient(credential)

# --- 3. CREATION FUNCTION ---
async def create_entra_user(user_data: UserModel) -> str:
    """Creates the user in Entra ID and returns the new user's object id."""
    new_user = User(
        display_name=user_data.display_name,
        given_name=user_data.given_name,
        surname=user_data.surname,
        mail_nickname=user_data.mail_nickname,
        user_principal_name=user_data.user_principal_name,
        department=user_data.department,
        job_title=user_data.job_title,
        usage_location=user_data.usage_location,
        account_enabled=True,
        password_profile=PasswordProfile(
            force_change_password_next_sign_in=True,
            password=user_data.password
        )
    )
    created_user = await client.users.post(new_user)
    return created_user.id

async def assign_manager(user_id: str, manager_id: str):
    """Sets the manager relationship via a separate Graph call, as required for this property."""
    ref = ReferenceUpdate(
        odata_id=f"https://graph.microsoft.com/v1.0/users/{manager_id}"
    )
    await client.users.by_user_id(user_id).manager.ref.put(ref)

async def main():
    logging.info("Starting Identity Automation (Restored Version) ---")

    upn_to_id: dict[str, str] = {}
    pending_managers: list[tuple[str, str]] = []  # (user_id, manager_upn)

    try:
        with open('users.csv', mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    user_model = UserModel(**row)

                    logging.info(f"Creating Account: {user_model.display_name}...")
                    user_id = await create_entra_user(user_model)
                    upn_to_id[user_model.user_principal_name.lower()] = user_id
                    logging.info(f"SUCCESS: {user_model.display_name} created.")

                    if user_model.manager_upn:
                        pending_managers.append((user_id, user_model.manager_upn.lower()))

                except ValidationError as ve:
                    logging.warning(f"[SKIP] CSV Validation Error: {ve.errors()[0]['msg']}")
                except Exception as e:
                    logging.error(f"FAILED to create user: {e}")

        for user_id, manager_upn in pending_managers:
            manager_id = upn_to_id.get(manager_upn)
            if not manager_id:
                logging.warning(f"[SKIP] Manager '{manager_upn}' not found among created users.")
                continue
            try:
                await assign_manager(user_id, manager_id)
                logging.info(f"SUCCESS: Manager assigned for user {user_id}.")
            except Exception as e:
                logging.error(f"FAILED to assign manager for user {user_id}: {e}")

    except FileNotFoundError:
        logging.critical("CRITICAL ERROR: users.csv missing.")

if __name__ == "__main__":
    asyncio.run(main())