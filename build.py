import json
import os
import re
import urllib.parse
import shutil

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'public') # Vercel needs 'public'
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')

# --- HELPER: Phone Number Cleaner ---
def clean_phone_for_whatsapp(phone):
    return re.sub(r'[^0-9]', '', phone)

# --- HELPER: Generate VCF (Contact File) ---
def generate_vcard(user):
    # This creates the file that allows "Save to Contacts"
    return f"""BEGIN:VCARD
VERSION:3.0
FN:{user['name']}
ORG:{user['company']}
TITLE:{user['position']}
TEL;TYPE=WORK,VOICE:{user['phone']}
EMAIL:{user['email']}
URL:{user['website']}
NOTE:{user.get('bio', '').replace('<br>', ' ')} 
END:VCARD"""

# --- HELPER: Smart Image Finder ---
def find_and_copy_image(user_filename, destination_folder):
    """
    Looks for the image in photos/. 
    If exact name fails, tries other extensions (png, jpg, jpeg).
    Returns the ACTUAL filename found, or None if missing.
    """
    
    # 1. If it's a URL (http...), just return it. We don't copy.
    if user_filename.startswith('http'):
        return user_filename

    # 2. Check for the exact file first
    src = os.path.join(PHOTOS_DIR, user_filename)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(destination_folder, user_filename))
        return user_filename

    # 3. Smart Search: Ignore the extension in JSON and look for matches
    name_without_ext = os.path.splitext(user_filename)[0]
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    
    for ext in allowed_extensions:
        test_name = name_without_ext + ext
        test_src = os.path.join(PHOTOS_DIR, test_name)
        
        if os.path.exists(test_src):
            print(f"   💡 Auto-corrected {user_filename} -> {test_name}")
            shutil.copy(test_src, os.path.join(destination_folder, test_name))
            return test_name # Return the NEW correct filename

    return None # Image not found

# --- MAIN SCRIPT ---
def main():
    json_path = os.path.join(BASE_DIR, 'data.json')
    template_path = os.path.join(BASE_DIR, 'template.html')

    print("🔨 Building cards for Vercel...")

    # Load Data
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print("❌ Error: Missing data.json or template.html")
        return

    # Clean Output Directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # Process Each User
    for user in users:
        user_folder = os.path.join(OUTPUT_DIR, user['id'])
        os.makedirs(user_folder)

        # --- 1. Handle Image (Smart Copy) ---
        original_photo_name = user['photo_url']
        final_photo_name = find_and_copy_image(original_photo_name, user_folder)
        
        if final_photo_name is None:
            print(f"⚠️  Warning: Could not find photo for {user['name']} (Checked {original_photo_name} and variants)")
            final_photo_name = "default.png" # Fallback if you have one
        
        # --- 2. Prepare Data for HTML ---
        whatsapp_num = clean_phone_for_whatsapp(user['phone'])
        
        # Location Button Logic
        if user.get('location_url'):
            loc_btn = f'''<a href="{user['location_url']}" target="_blank" class="btn btn-outline"><i class="fas fa-map-marker-alt" style="color:#db4437"></i> Direction</a>'''
        else:
            loc_btn = ""

        # Payment Button Logic
        if user.get('upi_id'):
            safe_name = urllib.parse.quote(user['name'])
            upi_link = f"upi://pay?pa={user['upi_id']}&pn={safe_name}&cu=INR"
            pay_btn = f'''<a href="{upi_link}" class="btn btn-payment"><i class="fab fa-google-pay" style="color:#4285F4"></i> Pay / UPI</a>'''
        else:
            pay_btn = ""

        # --- 3. Render HTML ---
        html_content = template

        # Handle Conditionals
        if not user.get('location_text'):
             html_content = html_content.replace('{% if location_text %}', '')
        else:
            html_content = html_content.replace('{% if location_text %}', '').replace('{% endif %}', '')

        if not user.get('location_url'):
             html_content = html_content.replace('{% if location_url %}', '')
        else:
            html_content = html_content.replace('{% if location_url %}', '').replace('{% endif %}', '')

        # Replacements
        for key in ['name', 'position', 'company', 'bio', 'phone', 'email', 'website', 'location_text', 'theme_color']:
            val = str(user.get(key, ''))
            html_content = html_content.replace(f'{{{{ {key} }}}}', val)
            
        # IMPORTANT: Use final_photo_name (which might be .png even if json said .jpg)
        html_content = html_content.replace('{{ photo_url }}', final_photo_name)
        html_content = html_content.replace('{{ whatsapp_clean }}', whatsapp_num)
        html_content = html_content.replace('{{ location_button }}', loc_btn)
        html_content = html_content.replace('{{ payment_button }}', pay_btn)

        # --- 4. Save Files ---
        # Save index.html
        with open(os.path.join(user_folder, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Save contact.vcf
        with open(os.path.join(user_folder, 'contact.vcf'), 'w', encoding='utf-8') as f:
            f.write(generate_vcard(user))

        print(f"   ✅ Generated: {user['name']} (Image: {final_photo_name})")

    print("\n🎉 Build Complete! Ready to push to GitHub.")

if __name__ == "__main__":
    main()