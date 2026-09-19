import json
import os
import re
import urllib.parse
import shutil
import hashlib


static_dir = './static_pages'
output_dir = './public' 

print("\n--- Starting Static File Copy ---")

if not os.path.exists(static_dir):
    print(f"❌ ERROR: Could not find the folder '{static_dir}'.")
    print("Check: Are you running this script from the main project folder? Is the folder named exactly 'static_pages'?")
else:
    print(f"✅ Found '{static_dir}'. Looking for files...")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created missing '{output_dir}' folder.")

    files_copied = 0
    for filename in os.listdir(static_dir):
        source_file = os.path.join(static_dir, filename)
        dest_file = os.path.join(output_dir, filename)
        
        if os.path.isfile(source_file):
            shutil.copy2(source_file, dest_file)
            print(f"➡️ Copied: {filename}")
            files_copied += 1
            
    print(f"--- Finished! Copied {files_copied} files. ---\n")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'public')
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')
STATE_FILE = os.path.join(BASE_DIR, 'build_state.json')

def clean_phone(phone):
    return re.sub(r'[^0-9]', '', phone)

def get_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def find_image(filename, dest):
    if not filename: return None
    if filename.startswith('http'): return filename
    
    src = os.path.join(PHOTOS_DIR, filename)
    if os.path.exists(src):
        dest_path = os.path.join(dest, filename)
        if not os.path.exists(dest_path):
            shutil.copy(src, dest_path)
        return filename
        
    name = os.path.splitext(filename)[0]
    for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']:
        if os.path.exists(os.path.join(PHOTOS_DIR, name + ext)):
            dest_path = os.path.join(dest, name + ext)
            if not os.path.exists(dest_path):
                shutil.copy(os.path.join(PHOTOS_DIR, name + ext), dest_path)
            return name + ext
    return None

def generate_vcard(user):
    # Support both string and list for phone
    phones = user['phone']
    if isinstance(phones, str):
        phones = [phones]

    # Support both string and list for email
    emails = user.get('email', '')
    if isinstance(emails, str):
        emails = [emails] if emails else []

    phone_lines = "\n".join([f"TEL;TYPE=WORK,VOICE:{p}" for p in phones])
    email_lines = "\n".join([f"EMAIL:{e.strip()}" for e in emails if e.strip()])

    social_notes = ""
    if user.get('linkedin'): social_notes += f"LinkedIn: {user['linkedin']} "

    return f"""BEGIN:VCARD
VERSION:3.0
FN:{user['name']}
ORG:{user['company']}
TITLE:{user['position']}
{phone_lines}
{email_lines}
URL:{user['website']}
NOTE:{user.get('bio', '').replace('<br>', ' ')} {social_notes}
END:VCARD"""

def generate_socials(user):
    platforms = {
        'instagram': 'fab fa-instagram',
        'facebook': 'fab fa-facebook-f',
        'linkedin': 'fab fa-linkedin-in',
        'twitter': 'fab fa-x-twitter',
        'youtube': 'fab fa-youtube'
    }
    html = '<div class="social-section">'
    has_links = False
    for key, icon in platforms.items():
        if user.get(key) and user[key].strip():
            html += f'<a href="{user[key]}" target="_blank" class="social-icon"><i class="{icon}"></i></a>'
            has_links = True
    html += '</div>'
    return html if has_links else ""

def generate_contact_list(user):
    items = []

    # --- PHONE (supports string or list) ---
    phones = user['phone']
    if isinstance(phones, str):
        phones = [phones]

    for phone in phones:
        if phone.strip():
            display_phone = phone.replace('+91', '+91 ')
            items.append(f'''
    <li class="contact-item">
        <a href="tel:{phone}" class="contact-link">
            <div class="icon-box"><i class="fas fa-phone"></i></div>
            <span>{display_phone}</span>
        </a>
    </li>''')

    # --- WHATSAPP (first number only) ---
    clean_wa = clean_phone(phones[0])
    items.append(f'''
    <li class="contact-item">
        <a href="https://wa.me/{clean_wa}" target="_blank" class="contact-link">
            <div class="icon-box"><i class="fab fa-whatsapp"></i></div>
            <span>WhatsApp</span>
        </a>
    </li>''')

    # --- EMAIL (supports string or list) ---
    emails = user.get('email', '')
    if isinstance(emails, str):
        emails = [emails] if emails else []

    for email in emails:
        if email.strip():
            items.append(f'''
    <li class="contact-item">
        <a href="mailto:{email.strip()}" class="contact-link">
            <div class="icon-box"><i class="fas fa-envelope"></i></div>
            <span>{email.strip()}</span>
        </a>
    </li>''')

    # --- WEBSITE ---
    if user.get('website'):
        items.append(f'''
    <li class="contact-item">
        <a href="{user['website']}" target="_blank" class="contact-link">
            <div class="icon-box"><i class="fas fa-globe"></i></div>
            <span>Website</span>
        </a>
    </li>''')

    # --- LOCATION ---
    if user.get('location_text'):
        text = user['location_text']
        url = user.get('location_url')
        if url:
            items.append(f'''
    <li class="contact-item">
        <a href="{url}" target="_blank" class="contact-link">
            <div class="icon-box"><i class="fas fa-map-marker-alt"></i></div>
            <span>{text}</span>
        </a>
    </li>''')
        else:
            items.append(f'''
    <li class="contact-item">
        <div class="contact-link">
            <div class="icon-box"><i class="fas fa-map-marker-alt"></i></div>
            <span>{text}</span>
        </div>
    </li>''')

    return "".join(items)

def main():
    try:
        with open(os.path.join(BASE_DIR, 'data.json'), 'r', encoding='utf-8') as f: users = json.load(f)
        with open(os.path.join(BASE_DIR, 'template.html'), 'r', encoding='utf-8') as f: template = f.read()
    except FileNotFoundError:
        print("❌ Error: Missing data.json or template.html")
        return

    # Load Memory (State)
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f: state = json.load(f)

    # Check if Template Changed
    current_template_hash = get_hash(template)
    template_changed = current_template_hash != state.get('template_hash')
    
    if template_changed:
        print("🎨 Template changed! Rebuilding everyone...")

    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

    new_state = {'template_hash': current_template_hash, 'users': {}}

    for user in users:
        u_dir = os.path.join(OUTPUT_DIR, user['id'])
        index_path = os.path.join(u_dir, 'index.html')
        
        user_data_string = json.dumps(user, sort_keys=True)
        user_hash = get_hash(user_data_string)
        
        new_state['users'][user['id']] = user_hash

        should_build = (
            template_changed or 
            state.get('users', {}).get(user['id']) != user_hash or
            not os.path.exists(index_path)
        )

        if should_build:
            if os.path.exists(u_dir): shutil.rmtree(u_dir)
            os.makedirs(u_dir)

            photo = find_image(user['photo_url'], u_dir)
            banner = find_image(user.get('banner_url'), u_dir)
            
            if banner:
                banner_css = f"background-image: url('{banner}'); background-size: cover; background-position: center;"
            else:
                banner_css = f"background: linear-gradient(135deg, {user.get('theme_color', '#333')}, #444);"

            loc_btn = ""
            if user.get('location_url'):
                loc_btn = f'''<a href="{user['location_url']}" target="_blank" class="btn btn-outline"><i class="fas fa-map-marker-alt" style="color:#db4437"></i> Direction</a>'''
            
            pay_btn = ""
            if user.get('upi_id'):
                pay_link = f"upi://pay?pa={user['upi_id']}&pn={urllib.parse.quote(user['name'])}&cu=INR"
                pay_btn = f'''<a href="{pay_link}" class="btn btn-payment"><i class="fab fa-google-pay" style="color:#4285F4"></i> Pay</a>'''

            catalogue_btn = ""
            if user.get('catalogue_url'):
                catalogue_btn = f'''<a href="{user['catalogue_url']}" target="_blank" class="btn btn-outline" style="border-color:#0E82E3; color:#0E82E3;"><i class="fas fa-book-open"></i> Catalogue</a>'''

            contact_html = generate_contact_list(user)
            social_html = generate_socials(user)

            content = template
            replacements = {
                '{{ name }}': user['name'],
                '{{ position }}': user['position'],
                '{{ company }}': user['company'],
                '{{ bio }}': user.get('bio', ''),
                '{{ theme_color }}': user.get('theme_color', '#333'),
                '{{ photo_url }}': photo,
                '{{ banner_style }}': banner_css,
                '{{ location_button }}': loc_btn,
                '{{ payment_button }}': pay_btn,
                '{{ catalogue_button }}': catalogue_btn,
                '{{ contact_list }}': contact_html,
                '{{ social_section }}': social_html
            }

            for k, v in replacements.items():
                content = content.replace(k, str(v))

            with open(index_path, 'w', encoding='utf-8') as f: f.write(content)
            with open(os.path.join(u_dir, 'contact.vcf'), 'w', encoding='utf-8') as f:
                f.write(generate_vcard(user))

            print(f"🔄 Rebuilt {user['name']}")
        else:
            print(f"⏭️  Skipped {user['name']} (No changes)")

    # Save the new memory to file
    with open(STATE_FILE, 'w') as f: json.dump(new_state, f)

if __name__ == "__main__":
    main()