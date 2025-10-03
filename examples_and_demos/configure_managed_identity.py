#!/usr/bin/env python
"""
Configure managed identity authentication for storage account and Function App
"""

def show_managed_identity_setup():
    """Show step-by-step managed identity configuration"""
    print("=" * 80)
    print("🔐 CONFIGURE MANAGED IDENTITY FOR STORAGE ACCOUNT")
    print("=" * 80)
    print()
    
    print("📋 STEP 1: ENABLE MANAGED IDENTITY ON FUNCTION APP")
    print("=" * 50)
    print()
    
    cli_commands = """
# Enable system-assigned managed identity for your Function App
az functionapp identity assign \\
    --resource-group "FIS-Internal" \\
    --name "fisfunctionpoc"

# Get the managed identity principal ID (save this for next step)
PRINCIPAL_ID=$(az functionapp identity show \\
    --resource-group "FIS-Internal" \\
    --name "fisfunctionpoc" \\
    --query principalId -o tsv)

echo "Function App Principal ID: $PRINCIPAL_ID"
"""
    
    print(cli_commands)
    
    print("\n📋 STEP 2: GRANT STORAGE PERMISSIONS TO FUNCTION APP")
    print("=" * 50)
    print()
    
    storage_commands = """
# Get your storage account resource ID
STORAGE_ID=$(az storage account show \\
    --name "fisdstoolkit" \\
    --resource-group "FIS-Internal" \\
    --query id -o tsv)

# Grant Storage Blob Data Contributor role to Function App
az role assignment create \\
    --role "Storage Blob Data Contributor" \\
    --assignee $PRINCIPAL_ID \\
    --scope $STORAGE_ID

# Grant Storage Account Contributor role (needed for container operations)
az role assignment create \\
    --role "Storage Account Contributor" \\
    --assignee $PRINCIPAL_ID \\
    --scope $STORAGE_ID

# Optionally, grant Storage Queue Data Contributor if using queues
az role assignment create \\
    --role "Storage Queue Data Contributor" \\
    --assignee $PRINCIPAL_ID \\
    --scope $STORAGE_ID
"""
    
    print(storage_commands)
    
    print("\n📋 STEP 3: UPDATE FUNCTION APP STORAGE CONNECTION")
    print("=" * 50)
    print()
    
    connection_commands = """
# Update Function App to use managed identity for storage
az functionapp config appsettings set \\
    --resource-group "FIS-Internal" \\
    --name "fisfunctionpoc" \\
    --settings AzureWebJobsStorage__accountname="fisdstoolkit"

# Remove the old connection string (if it exists)
az functionapp config appsettings delete \\
    --resource-group "FIS-Internal" \\
    --name "fisfunctionpoc" \\
    --setting-names "AzureWebJobsStorage"

# Verify the settings
az functionapp config appsettings list \\
    --resource-group "FIS-Internal" \\
    --name "fisfunctionpoc" \\
    --query "[?name=='AzureWebJobsStorage__accountname']"
"""
    
    print(connection_commands)
    
    print("\n📋 STEP 4: ALTERNATIVE - ENABLE KEY ACCESS ON STORAGE")
    print("=" * 50)
    print("(If you prefer to keep using keys temporarily)")
    print()
    
    key_enable_commands = """
# Enable key-based access on storage account (less secure but simpler)
az storage account update \\
    --name "fisdstoolkit" \\
    --resource-group "FIS-Internal" \\
    --allow-shared-key-access true

# Then you can continue using connection strings
"""
    
    print(key_enable_commands)

def create_complete_deployment_script():
    """Create a complete deployment script with managed identity"""
    print("\n" + "=" * 80)
    print("🚀 COMPLETE DEPLOYMENT SCRIPT WITH MANAGED IDENTITY")
    print("=" * 80)
    print()
    
    complete_script = """#!/bin/bash

# Complete deployment script with managed identity setup
set -e

echo "🚀 Starting complete deployment with managed identity..."

# Variables
RESOURCE_GROUP="FIS-Internal"
FUNCTION_APP_NAME="fisfunctionpoc"
STORAGE_ACCOUNT="fisdstoolkit"

echo "📋 Step 1: Enable managed identity on Function App..."
az functionapp identity assign \\
    --resource-group "$RESOURCE_GROUP" \\
    --name "$FUNCTION_APP_NAME"

echo "📋 Step 2: Get principal ID..."
PRINCIPAL_ID=$(az functionapp identity show \\
    --resource-group "$RESOURCE_GROUP" \\
    --name "$FUNCTION_APP_NAME" \\
    --query principalId -o tsv)

echo "Function App Principal ID: $PRINCIPAL_ID"

echo "📋 Step 3: Get storage account ID..."
STORAGE_ID=$(az storage account show \\
    --name "$STORAGE_ACCOUNT" \\
    --resource-group "$RESOURCE_GROUP" \\
    --query id -o tsv)

echo "📋 Step 4: Grant storage permissions..."
az role assignment create \\
    --role "Storage Blob Data Contributor" \\
    --assignee "$PRINCIPAL_ID" \\
    --scope "$STORAGE_ID"

az role assignment create \\
    --role "Storage Account Contributor" \\
    --assignee "$PRINCIPAL_ID" \\
    --scope "$STORAGE_ID"

echo "📋 Step 5: Update Function App storage connection..."
az functionapp config appsettings set \\
    --resource-group "$RESOURCE_GROUP" \\
    --name "$FUNCTION_APP_NAME" \\
    --settings AzureWebJobsStorage__accountname="$STORAGE_ACCOUNT"

echo "📋 Step 6: Deploy function code..."
az functionapp deployment source config-zip \\
    --resource-group "$RESOURCE_GROUP" \\
    --name "$FUNCTION_APP_NAME" \\
    --src image_processing_functions.zip

echo "📋 Step 7: Configure application settings..."
az functionapp config appsettings set \\
    --resource-group "$RESOURCE_GROUP" \\
    --name "$FUNCTION_APP_NAME" \\
    --settings @function_app_settings.json

echo "✅ Deployment completed successfully!"
echo "📊 Verifying functions..."
az functionapp function list \\
    --resource-group "$RESOURCE_GROUP" \\
    --name "$FUNCTION_APP_NAME" \\
    --query "[].name" -o table

echo "🎉 All done! Your image processing functions are deployed with managed identity."
"""
    
    with open("complete_deployment_with_managed_identity.sh", "w") as f:
        f.write(complete_script)
    
    print("✅ Complete deployment script saved to: complete_deployment_with_managed_identity.sh")
    print("📄 Make it executable: chmod +x complete_deployment_with_managed_identity.sh")
    print("🚀 Run it: ./complete_deployment_with_managed_identity.sh")

def show_portal_alternative():
    """Show Portal steps for managed identity"""
    print("\n" + "=" * 80)
    print("🌐 AZURE PORTAL ALTERNATIVE")
    print("=" * 80)
    print()
    
    portal_steps = """
📋 AZURE PORTAL STEPS FOR MANAGED IDENTITY:

1. 🔐 ENABLE MANAGED IDENTITY ON FUNCTION APP:
   • Go to your Function App "fisfunctionpoc" in Azure Portal
   • Click "Identity" in the left menu
   • Under "System assigned" tab, turn Status "On"
   • Click "Save" and note the Object (principal) ID

2. 🗃️  GRANT STORAGE PERMISSIONS:
   • Go to your Storage Account "fisdstoolkit"
   • Click "Access Control (IAM)" in the left menu
   • Click "Add" → "Add role assignment"
   • Select "Storage Blob Data Contributor" role
   • In "Assign access to", select "Managed identity"
   • Select your Function App from the list
   • Click "Review + assign"
   • Repeat for "Storage Account Contributor" role

3. 🔧 UPDATE FUNCTION APP STORAGE CONNECTION:
   • Go back to your Function App
   • Click "Configuration" in the left menu
   • Find "AzureWebJobsStorage" setting
   • Change its value to: fisdstoolkit
   • Or add new setting "AzureWebJobsStorage__accountname" = "fisdstoolkit"
   • Click "Save"

4. 🚀 DEPLOY FUNCTIONS:
   • Go to "Deployment Center"
   • Use "ZIP Deploy" with the image_processing_functions.zip file
   • Add the application settings from function_app_settings.json

5. ✅ VERIFY:
   • Check "Functions" menu for the new functions
   • Test one function to ensure it works
"""
    
    print(portal_steps)
    
    with open("portal_managed_identity_steps.txt", "w") as f:
        f.write(portal_steps)
    
    print("📄 Portal steps saved to: portal_managed_identity_steps.txt")

if __name__ == "__main__":
    print("🔐 MANAGED IDENTITY CONFIGURATION GUIDE")
    print()
    
    show_managed_identity_setup()
    create_complete_deployment_script()
    show_portal_alternative()
    
    print("\n" + "=" * 80)
    print("📋 SUMMARY - TWO OPTIONS")
    print("=" * 80)
    print()
    print("🎯 OPTION 1: Managed Identity (Recommended - More Secure)")
    print("   • Run: ./complete_deployment_with_managed_identity.sh")
    print("   • Or follow the Portal steps in portal_managed_identity_steps.txt")
    print()
    print("⚡ OPTION 2: Quick Fix (Enable Key Access Temporarily)")
    print("   • Run: az storage account update --name fisdstoolkit --resource-group FIS-Internal --allow-shared-key-access true")
    print("   • Then deploy normally with: bash azure_cli_deployment.sh")
    print()
    print("💡 I recommend Option 1 for production security!")