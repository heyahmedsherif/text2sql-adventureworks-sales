#!/usr/bin/env python
"""
Deploy image processing functions manually to Azure Function App
"""
import os
import json
import subprocess
import sys
from pathlib import Path

def create_function_manually(function_name, function_code, function_json):
    """Create a single function manually"""
    print(f"🔧 Creating function: {function_name}")
    
    # Create function.json content
    function_config = {
        "scriptFile": "__init__.py",
        "bindings": [
            {
                "authLevel": "function",
                "type": "httpTrigger",
                "direction": "in",
                "name": "req",
                "methods": ["post"]
            },
            {
                "type": "http",
                "direction": "out",
                "name": "$return"
            }
        ]
    }
    
    # Try to create function using Azure CLI extensions
    try:
        # This would require manual steps in Azure Portal
        print(f"   ⚠️  Function {function_name} needs manual creation in Portal")
        print(f"   📝 Copy the code to: Function App → Functions → + Create → HTTP trigger")
        print(f"   🔧 Function name: {function_name}")
        return False
    except Exception as e:
        print(f"   ❌ Failed to create {function_name}: {e}")
        return False

def deploy_via_portal_guide():
    """Create deployment guide for Azure Portal"""
    print("=" * 80)
    print("🌐 AZURE PORTAL DEPLOYMENT GUIDE")
    print("=" * 80)
    print()
    
    guide = """
📋 STEP-BY-STEP PORTAL DEPLOYMENT:

1. 🌐 Open Azure Portal (https://portal.azure.com)

2. 🔍 Navigate to Function App:
   • Search for "fisfunctionpoc"
   • Click on the Function App

3. 📁 Upload Functions Package:
   • Method 1 - Deployment Center:
     - Click "Deployment" → "Deployment Center" 
     - Choose "Local Git" or "Upload a .zip file"
     - Upload: image_processing_functions_v2.zip

   • Method 2 - Advanced Tools (Kudu):
     - Click "Development Tools" → "Advanced Tools" → "Go"
     - In Kudu, go to "Debug console" → "CMD"
     - Navigate to site/wwwroot
     - Drag and drop the zip file
     - Extract the contents

4. 🔧 Add Environment Variables:
   • Click "Configuration" → "Application settings"
   • Add each setting from image_processing_function_settings.json
   • Click "Save"

5. ✅ Verify Deployment:
   • Click "Functions" in left menu
   • Should see 5 new functions:
     - layout_analysis
     - figure_analysis  
     - layout_and_figure_merger
     - semantic_text_chunker
     - mark_up_cleaner

🎯 WHY PORTAL WORKS BETTER:
The Flex Consumption plan has restrictions on CLI deployment,
but the Portal interface handles these limitations automatically.
    """
    
    print(guide)
    
    # Write to file for reference
    with open("portal_deployment_steps.txt", "w") as f:
        f.write(guide)
    
    print("📄 Guide saved to: portal_deployment_steps.txt")

def create_environment_variables_script():
    """Create script to set environment variables"""
    print("\n" + "=" * 80)
    print("⚙️  ENVIRONMENT VARIABLES SETUP")
    print("=" * 80)
    print()
    
    # Load the settings
    try:
        with open("image_processing_function_settings.json", "r") as f:
            settings = json.load(f)
        
        print("📋 Environment variables to add in Portal:")
        print()
        
        for setting in settings:
            name = setting["name"]
            value = setting["value"]
            # Mask sensitive values
            if "key" in name.lower() or "connectionstring" in name.lower():
                masked_value = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
                print(f"   {name} = {masked_value}")
            else:
                print(f"   {name} = {value}")
        
        print()
        print("💡 Copy these to: Function App → Configuration → Application settings")
        
        # Create CLI commands for backup
        cli_commands = []
        setting_pairs = []
        for setting in settings:
            setting_pairs.append(f"{setting['name']}=\"{setting['value']}\"")
        
        # Split into chunks to avoid command length limits
        chunk_size = 10
        for i in range(0, len(setting_pairs), chunk_size):
            chunk = setting_pairs[i:i+chunk_size]
            cmd = f"az functionapp config appsettings set --resource-group \"FIS-Internal\" --name \"fisfunctionpoc\" --settings " + " ".join(chunk)
            cli_commands.append(cmd)
        
        # Save CLI commands to file
        with open("configure_function_app_settings.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Configure Function App settings for image processing\n\n")
            for cmd in cli_commands:
                f.write(cmd + "\n\n")
        
        print("📄 CLI backup commands saved to: configure_function_app_settings.sh")
        
        return True
        
    except FileNotFoundError:
        print("❌ Settings file not found: image_processing_function_settings.json")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in settings file")
        return False

def create_storage_containers_guide():
    """Create guide for storage container setup"""
    print("\n" + "=" * 80)
    print("📦 STORAGE CONTAINERS SETUP")
    print("=" * 80)
    print()
    
    containers_guide = """
📋 REQUIRED STORAGE CONTAINERS:

1. 🌐 Open Azure Portal → Storage Account "fisdstoolkit"

2. 📁 Create Containers:
   • Click "Containers" in left menu
   • Click "+ Container" for each:
     
     Container 1: "documents"
     - Name: documents
     - Public access level: Private (no anonymous access)
     - Purpose: Upload PDF/DOCX/PPTX files here
     
     Container 2: "documents-figures" 
     - Name: documents-figures
     - Public access level: Private (no anonymous access)
     - Purpose: Extracted figures/charts saved here
     
     Container 3: "rag-documents-index"
     - Name: rag-documents-index
     - Public access level: Private (no anonymous access)  
     - Purpose: AI Search processing artifacts

3. ✅ Verification:
   • Should see 3 new containers in the list
   • All should show "Private" access level

💡 ALTERNATIVE - CLI Method:
If you have proper permissions, run these commands:

az storage container create --account-name fisdstoolkit --name documents --auth-mode login
az storage container create --account-name fisdstoolkit --name documents-figures --auth-mode login  
az storage container create --account-name fisdstoolkit --name rag-documents-index --auth-mode login
    """
    
    print(containers_guide)
    
    with open("storage_containers_setup.txt", "w") as f:
        f.write(containers_guide)
    
    print("📄 Guide saved to: storage_containers_setup.txt")

def test_function_app_access():
    """Test if we can access the Function App"""
    print("\n" + "=" * 80)
    print("🧪 TESTING FUNCTION APP ACCESS")
    print("=" * 80)
    print()
    
    try:
        # Test basic Function App access
        result = subprocess.run([
            "az", "functionapp", "show", 
            "--resource-group", "FIS-Internal",
            "--name", "fisfunctionpoc",
            "--query", "{state: state, kind: kind, sku: sku.tier}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            print("✅ Function App Status:")
            print(f"   State: {info.get('state', 'Unknown')}")
            print(f"   Kind: {info.get('kind', 'Unknown')}")
            print(f"   SKU: {info.get('sku', 'Unknown')}")
            print()
            
            # Check current functions
            func_result = subprocess.run([
                "az", "functionapp", "function", "list",
                "--resource-group", "FIS-Internal", 
                "--name", "fisfunctionpoc",
                "--query", "[].name"
            ], capture_output=True, text=True)
            
            if func_result.returncode == 0:
                functions = json.loads(func_result.stdout)
                print(f"📊 Current functions: {len(functions)}")
                if functions:
                    for func in functions:
                        print(f"   • {func}")
                else:
                    print("   (No functions currently deployed)")
                print()
            
            return True
        else:
            print(f"❌ Cannot access Function App: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Function App: {e}")
        return False

def main():
    """Main deployment coordination"""
    print("🚀 IMAGE PROCESSING FUNCTIONS DEPLOYMENT")
    print("   Deploying to Azure Function App: fisfunctionpoc")
    print()
    
    # Test Function App access
    if not test_function_app_access():
        print("❌ Cannot proceed - Function App access issues")
        return False
    
    # Create deployment guides
    deploy_via_portal_guide()
    create_environment_variables_script()
    create_storage_containers_guide()
    
    print("\n" + "=" * 80)
    print("🎯 DEPLOYMENT SUMMARY")
    print("=" * 80)
    print()
    print("✅ Files Ready:")
    print("   • image_processing_functions_v2.zip (Function code)")
    print("   • image_processing_function_settings.json (Environment vars)")
    print("   • portal_deployment_steps.txt (Portal guide)")
    print("   • configure_function_app_settings.sh (CLI backup)")
    print("   • storage_containers_setup.txt (Container setup)")
    print()
    print("🚀 Next Steps:")
    print("   1. Upload functions via Azure Portal (recommended)")
    print("   2. Add environment variables in Portal")
    print("   3. Create storage containers") 
    print("   4. Test deployed functions")
    print()
    print("💡 The Portal method works best for Flex Consumption plan")
    
    return True

if __name__ == "__main__":
    main()