import csv
import logging
import os
from datetime import datetime, timedelta, timezone
import config

# Azure & Microsoft Graph Imports
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient

# --- 1. LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("license_governance_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- 2. CONFIGURATION PARAMETERS ---
# CIS Control Threshold: Flag users inactive for over 90 days
INACTIVITY_THRESHOLD_DAYS = 90
INVENTORY_CSV = "license_inventory_summary.csv"
UTILIZATION_CSV = "user_license_utilization.csv"
RECLAMATION_LOG_CSV = "license_reclamation_audit.csv"

# --- 3. AUTHENTICATION ---
credential = ClientSecretCredential(
    tenant_id=config.TENANT_ID,
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET
)
client = GraphServiceClient(credential)

# --- 4. GOVERNANCE & REPORTING FUNCTIONS ---
async def generate_license_inventory_report() -> dict[str, str]:
    """Scans and exports the tenant-wide license balances to CSV."""
    logging.info("Analyzing tenant commercial license inventory pools...")
    product_map = {}
    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Get purchased subscription pools (SKUs)
        skus = await client.subscribed_skus.get()
        
        with open(INVENTORY_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["AuditTimestamp", "ProductName", "TotalPurchased", "TotalAssigned", "AvailableSeats"])
            
            for sku in skus.value:
                product_name = sku.sku_part_number  # e.g., "AAD_PREMIUM_P2"
                total_seats = sku.prepaid_units.enabled
                used_seats = sku.consumed_units
                available_seats = total_seats - used_seats
                
                # Save internal ID mapping for user processing step later
                product_map[str(sku.sku_id)] = product_name
                
                writer.writerow([report_date, product_name, total_seats, used_seats, available_seats])
                
        logging.info(f"SUCCESS: Exported overall balances to '{INVENTORY_CSV}'")
        return product_map
    except Exception as e:
        logging.error(f"FAILED to generate inventory summary: {e}")
        return {}

async def run_utilization_and_reclamation_pipeline(product_map: dict[str, str]):
    """Tracks active seats, removes inactive users from license groups, and logs audits."""
    logging.info("Scanning all directory accounts for active seat usage metrics...")
    
    # Calculate target threshold date
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=INACTIVITY_THRESHOLD_DAYS)
    
    try:
        # Request user profiles with active license strings and sign-in telemetry logs
        def configure_request(x):
            # 🚀 Added 'id' and 'department' to your parameters list so reclamation works
            x.query_parameters.select = [
                "id", "displayName", "userPrincipalName", "department", "assignedLicenses", "signInActivity"
            ]
            return x
        
        users = await client.users.get(request_configuration=configure_request)
        
        utilization_records = []
        reclamation_records = []
        audit_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        for user in users.value:
            if not user.assigned_licenses:
                continue  # Skip unassigned users
                
            # Extract last login date
            last_login_str = "NEVER"
            is_inactive = False
            
            if user.sign_in_activity and user.sign_in_activity.last_sign_in_date_time:
                last_login_date = user.sign_in_activity.last_sign_in_date_time
                last_login_str = last_login_date.strftime("%Y-%m-%d %H:%M:%S")
                if last_login_date < cutoff_date:
                    is_inactive = True
            else:
                # If no login activity exists, check if user was created long ago to prevent false alarms
                is_inactive = True

            # Match user license SKU arrays to descriptive product names
            for license_sku in user.assigned_licenses:
                sku_id_str = str(license_sku.sku_id)
                clean_product_name = product_map.get(sku_id_str, f"Unknown-{sku_id_str}")
                
                # Tag status simple and clear for non-technical readers
                account_status = "ACTIVE"
                if last_login_str == "NEVER":
                    account_status = "INACTIVE_NEVER_LOGGED_IN"
                elif is_inactive:
                    account_status = f"INACTIVE_OVER_{INACTIVITY_THRESHOLD_DAYS}_DAYS"
                
                utilization_records.append([
                    user.display_name,
                    user.user_principal_name,
                    clean_product_name,
                    last_login_str,
                    account_status
                ])
                
                # 🚀 LIVE AUTOMATED RECLAMATION BLOCK
                if is_inactive:
                    logging.warning(f"RECLAMATION TRIGGERED: Removing {user.user_principal_name} due to inactivity.")
                    
                    # Clean up user's department to look up group maps in config
                    dept_key = (user.department or "").lower().strip()
                    target_group_id = getattr(config, "GROUP_MAP", {}).get(dept_key) if hasattr(config, "GROUP_MAP") else None
                    
                    action_status = "FAILED_NO_GROUP_MAPPED"
                    if target_group_id:
                        try:
                            # Send a request to delete the user out of the license-delivery group
                            await client.groups.by_group_id(target_group_id).members.by_directory_object_id(user.id).ref.delete()
                            action_status = "RECLAIMED_SUCCESS"
                            logging.info(f"SUCCESS: Pulled back license seat from {user.user_principal_name}.")
                        except Exception as api_err:
                            action_status = f"FAILED_API_ERROR: {str(api_err)}"
                            logging.error(f"API Error removing user from group {target_group_id}: {api_err}")
                    
                    reclamation_records.append([
                        audit_time,
                        user.display_name,
                        user.user_principal_name,
                        clean_product_name,
                        last_login_str,
                        action_status
                    ])

        # Save active matrix tracking sheet
        with open(UTILIZATION_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["DisplayName", "UserPrincipalName", "AssignedProduct", "LastSignInDate", "Status"])
            writer.writerows(utilization_records)
        logging.info(f"SUCCESS: Exported utilization data tracking matrix to '{UTILIZATION_CSV}'")
        
        # Save or append reclamation target action lists for audit sign-offs
        file_mode = "a" if os.path.exists(RECLAMATION_LOG_CSV) else "w"
        with open(RECLAMATION_LOG_CSV, mode=file_mode, newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if file_mode == "w":
                writer.writerow(["FlaggedTimestamp", "DisplayName", "UserPrincipalName", "ProductToReclaim", "LastSignIn", "ActionStatus"])
            if reclamation_records:
                writer.writerows(reclamation_records)
                logging.info(f"SUCCESS: Saved {len(reclamation_records)} reclamation execution logs to '{RECLAMATION_LOG_CSV}'")
            else:
                logging.info("Clean report check: Zero dormant licenses detected.")

    except Exception as e:
        logging.error(f"FAILED to process user licensing records: {e}")

async def main():
    logging.info("Starting Standardized License Governance Automation Pipeline ---")
    product_map = await generate_license_inventory_report()
    if product_map:
        await run_utilization_and_reclamation_pipeline(product_map)
    logging.info("License Governance Pipeline Execution Completed.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
