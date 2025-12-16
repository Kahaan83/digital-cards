import json
import os
import re
import urllib.parse
import shutil

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'public') 
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')

def clean_phone_for_whatsapp(phone):
    return re.sub(r'[^0-9]', '', phone)

def generate_vcard(user):
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

def find_and_copy_image(user_filename, destination_folder):
    # 1. If it's a URL, return as is
    if user_filename.startswith('http'):
        return user_filename

    # 2. Try exact match
    src = os.path.join(PHOTOS_DIR, user_filename)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(destination_folder, user_filename))
        return user_filename

    # 3. Smart Search (Try png/jpg/jpeg variations)
    name_without_ext = os.path.splitext(user_filename)[0]
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    
    for ext in allowed_extensions:
        test_name = name_without_ext + ext
        test_src = os.path.join(PHOTOS_DIR, test_name)
        
        if os.path.exists(test_src):
            print(f"   💡 Auto-corrected image: {user_filename} -> {test_name}")
            shutil.copy(test_src, os.path.join(destination_folder, test_name))
            return test_name 

    return "default.png" # Fallback

def main():
    json_path = os.path.join(BASE_DIR, 'data.json')
    template_path = os.path.join(BASE_DIR, 'template.html')

    print("🔨 Building cards...")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print("❌ Error: Missing data.json or template.html")
        return

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    for user in users:
        user_folder = os.path.join(OUTPUT_DIR, user['id'])
        os.makedirs(user_folder)

        # 1. Handle Image
        final_photo_name = find_and_copy_image(user['photo_url'], user_folder)
        
        # 2. Process Data
        whatsapp_num = clean_phone_for_whatsapp(user['phone'])
        
        # Location Button
        if user.get('location_url'):
            loc_btn = f'''<a href="{user['location_url']}" target="_blank" class="btn btn-outline"><i class="fas fa-map-marker-alt" style="color:#db4437"></i> Direction</a>'''
        else:
            loc_btn = ""

        # Payment Button
        if user.get('upi_id'):
            safe_name = urllib.parse.quote(user['name'])
            upi_link = f"upi://pay?pa={user['upi_id']}&pn={safe_name}&cu=INR"
            pay_btn = f'''<a href="{upi_link}" class="btn btn-payment"><i class="fab fa-google-pay" style="color:#4285F4"></i> Pay / UPI</a>'''
        else:
            pay_btn = ""

        # 3. Render HTML
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
            
        html_content = html_content.replace('{{ photo_url }}', final_photo_name)
        html_content = html_content.replace('{{ whatsapp_clean }}', whatsapp_num)
        html_content = html_content.replace('{{ location_button }}', loc_btn)
        html_content = html_content.replace('{{ payment_button }}', pay_btn)

        # 4. Save Files
        with open(os.path.join(user_folder, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)

        with open(os.path.join(user_folder, 'contact.vcf'), 'w', encoding='utf-8') as f:
            f.write(generate_vcard(user))

        print(f"   ✅ Generated: {user['name']} (Img: {final_photo_name})")

    print("\n🎉 Build Complete!")

if __name__ == "__main__":
    main()