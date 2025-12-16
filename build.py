import json
import os
import re
import urllib.parse
import shutil

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Vercel looks for a 'public' folder by default, so we output there.
OUTPUT_DIR = os.path.join(BASE_DIR, 'public')
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')

# --- HELPER FUNCTIONS ---
def clean_phone_for_whatsapp(phone):
    return re.sub(r'[^0-9]', '', phone)

def generate_vcard(user):
    # Generates the contact file that phones can download
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

def main():
    json_path = os.path.join(BASE_DIR, 'data.json')
    template_path = os.path.join(BASE_DIR, 'template.html')

    print("🔨 Building cards for Vercel...")

    # 1. Load Data
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print("❌ Error: Missing data.json or template.html")
        return

    # 2. Clean & Recreate Output Directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # 3. Process Each User
    for user in users:
        user_folder = os.path.join(OUTPUT_DIR, user['id'])
        os.makedirs(user_folder)

        # --- Image Logic ---
        image_filename = user['photo_url']
        # If it's a local file (not a URL), copy it to the user's folder
        if not image_filename.startswith('http'):
            src = os.path.join(PHOTOS_DIR, image_filename)
            dst = os.path.join(user_folder, image_filename)
            if os.path.exists(src):
                shutil.copy(src, dst)
            else:
                print(f"⚠️  Warning: Image {image_filename} not found in photos folder.")

        # --- Button Logic ---
        whatsapp_num = clean_phone_for_whatsapp(user['phone'])
        
        # Location Button
        if user.get('location_url'):
            loc_btn = f'''<a href="{user['location_url']}" target="_blank" class="btn btn-outline"><i class="fas fa-map-marker-alt" style="color:#db4437"></i> Direction</a>'''
        else:
            loc_btn = ""

        # UPI / Payment Button
        if user.get('upi_id'):
            safe_name = urllib.parse.quote(user['name'])
            upi_link = f"upi://pay?pa={user['upi_id']}&pn={safe_name}&cu=INR"
            pay_btn = f'''<a href="{upi_link}" class="btn btn-payment"><i class="fab fa-google-pay" style="color:#4285F4"></i> Pay / UPI</a>'''
        else:
            pay_btn = ""

        # --- HTML Rendering ---
        html_content = template

        # Handle Conditionals (Remove empty blocks if data is missing)
        if not user.get('location_text'):
             html_content = html_content.replace('{% if location_text %}', '')
        else:
            html_content = html_content.replace('{% if location_text %}', '').replace('{% endif %}', '')

        if not user.get('location_url'):
             html_content = html_content.replace('{% if location_url %}', '')
        else:
            html_content = html_content.replace('{% if location_url %}', '').replace('{% endif %}', '')

        # Replace placeholders with actual data
        for key in ['name', 'position', 'company', 'bio', 'phone', 'email', 'website', 'location_text', 'theme_color']:
            val = str(user.get(key, ''))
            html_content = html_content.replace(f'{{{{ {key} }}}}', val)
            
        html_content = html_content.replace('{{ photo_url }}', image_filename)
        html_content = html_content.replace('{{ whatsapp_clean }}', whatsapp_num)
        html_content = html_content.replace('{{ location_button }}', loc_btn)
        html_content = html_content.replace('{{ payment_button }}', pay_btn)

        # --- Save Files ---
        # 1. index.html (The Card)
        with open(os.path.join(user_folder, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 2. contact.vcf (The "Save Contact" File)
        with open(os.path.join(user_folder, 'contact.vcf'), 'w', encoding='utf-8') as f:
            f.write(generate_vcard(user))

        print(f"   ✅ Generated: {user['name']}")

    print("\n🎉 Build Complete! Ready to push to GitHub.")

if __name__ == "__main__":
    main()