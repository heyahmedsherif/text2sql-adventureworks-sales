#!/usr/bin/env python
"""
Create storage containers required for image processing
"""
import os
import subprocess

def create_storage_containers():
    """Create required storage containers for image processing"""
    print("=" * 80)
    print("📦 CREATING IMAGE PROCESSING STORAGE CONTAINERS")
    print("=" * 80)
    print()
    
    containers = [
        {
            "name": "documents", 
            "description": "Main container for uploaded documents (PDF/DOCX/PPTX)",
            "public_access": "off"
        },
        {
            "name": "documents-figures", 
            "description": "Container for extracted figures and charts from documents",
            "public_access": "off"
        },
        {
            "name": "rag-documents-index",
            "description": "Container for AI Search document processing artifacts", 
            "public_access": "off"
        }
    ]
    
    storage_account = "fisdstoolkit"
    resource_group = "FIS-Internal"
    
    print(f"🏪 Storage Account: {storage_account}")
    print(f"📁 Resource Group: {resource_group}")
    print()
    
    success_containers = []
    existing_containers = []
    failed_containers = []
    
    for container in containers:
        container_name = container["name"]
        description = container["description"]
        
        print(f"📦 Creating container: {container_name}")
        print(f"   📝 Purpose: {description}")
        
        # Try creating the container with managed identity
        try:
            result = subprocess.run([
                "az", "storage", "container", "create",
                "--account-name", storage_account,
                "--name", container_name,
                "--auth-mode", "login",
                "--public-access", container["public_access"]
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"   ✅ Container '{container_name}' created successfully")
                success_containers.append(container_name)
            else:
                # Check if it already exists
                if "already exists" in result.stderr:
                    print(f"   ✅ Container '{container_name}' already exists")
                    existing_containers.append(container_name)
                else:
                    print(f"   ❌ Failed to create '{container_name}': {result.stderr}")
                    failed_containers.append(container_name)
                    
        except subprocess.TimeoutExpired:
            print(f"   ⏱️ Timeout creating '{container_name}' - may need manual creation")
            failed_containers.append(container_name)
        except Exception as e:
            print(f"   ❌ Error creating '{container_name}': {e}")
            failed_containers.append(container_name)
        
        print()
    
    # Summary
    print("=" * 80)
    print("📊 CONTAINER CREATION SUMMARY")
    print("=" * 80)
    print()
    
    if success_containers:
        print("✅ SUCCESSFULLY CREATED:")
        for container in success_containers:
            print(f"   • {container}")
        print()
    
    if existing_containers:
        print("✅ ALREADY EXISTED:")
        for container in existing_containers:
            print(f"   • {container}")
        print()
    
    if failed_containers:
        print("❌ FAILED TO CREATE:")
        for container in failed_containers:
            print(f"   • {container}")
        print()
        print("💡 MANUAL CREATION NEEDED:")
        print("   1. Go to Azure Portal")
        print("   2. Navigate to Storage Account 'fisdstoolkit'")
        print("   3. Click 'Containers' in left menu")
        print("   4. Click '+ Container' to create each missing container")
        print()
    
    total_ready = len(success_containers) + len(existing_containers)
    total_containers = len(containers)
    
    print(f"📈 PROGRESS: {total_ready}/{total_containers} containers ready")
    
    if total_ready == total_containers:
        print("🎉 All storage containers are ready for image processing!")
        return True
    else:
        print("⚠️  Some containers need manual creation via Azure Portal")
        return False

def show_portal_instructions():
    """Show instructions for manual container creation"""
    print()
    print("=" * 80)
    print("🖱️  MANUAL CONTAINER CREATION VIA AZURE PORTAL")
    print("=" * 80)
    print()
    
    instructions = """
📝 STEP-BY-STEP INSTRUCTIONS:

1. 🌐 Open Azure Portal (https://portal.azure.com)

2. 🔍 Search for "fisdstoolkit" storage account

3. 📂 Navigate to Containers:
   • Click on "fisdstoolkit" storage account
   • In the left menu, click "Containers"

4. ➕ Create each container:
   • Click "+ Container" button
   • Enter container name
   • Set Public access level to "Private"
   • Click "Create"

📦 CONTAINERS TO CREATE:
   • documents (for uploaded documents)
   • documents-figures (for extracted figures)
   • rag-documents-index (for AI Search artifacts)

5. ✅ Verify all containers exist in the list

💡 ALTERNATIVE - Azure CLI:
If portal doesn't work, you can also try Azure Cloud Shell:
   • Click the Cloud Shell icon (>_) in Azure Portal
   • Run: az storage container create --account-name fisdstoolkit --name documents --auth-mode login
   • Repeat for each container name
"""
    
    print(instructions)

if __name__ == "__main__":
    print("📦 IMAGE PROCESSING STORAGE SETUP")
    print()
    
    success = create_storage_containers()
    
    if not success:
        show_portal_instructions()
    
    print()
    print("🚀 NEXT: Deploy image processing functions to Function App")
    print("   Use the existing 'fisfunctionpoc' Function App for deployment")