import json
import os
import re
import urllib.parse
import shutil
import hashlib  # <--- New Tool for creating fingerprints

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'public')
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')
STATE_FILE = os.path.join(BASE_DIR, 'build_state.json') # <--- Stores the memory

def clean_phone(phone):
    return re.sub(r'[^0-9]', '', phone)

# Helper to create a unique fingerprint (Hash) from text
def get_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def find_image(filename, dest):
    if not filename: return None
    if filename.startswith('http'): return filename
    
    src = os.path.join(PHOTOS_DIR, filename)
    if os.path.exists(src):
        # Only copy if destination doesn't exist or file changed
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
    social_notes = ""
    if user.get('linkedin'): social_notes += f"LinkedIn: {user['linkedin']} "
    return f"""BEGIN:VCARD
VERSION:3.0
FN:{user['name']}
ORG:{user['company']}
TITLE:{user['position']}
TEL;TYPE=WORK,VOICE:{user['phone']}
EMAIL:{user['email']}
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
        if user.get(key):
            html += f'<a href="{user[key]}" target="_blank" class="social-icon"><i class="{icon}"></i></a>'
            has_links = True
    html += '</div>'
    return html if has_links else ""

def generate_contact_list(user):
    items = []
    display_phone = user['phone'].replace('+91', '+91 ')
    items.append(f'''
    <li class="contact-item">
        <a href="tel:{user['phone']}" class="contact-link">
            <div class="icon-box"><i class="fas fa-phone"></i></div>
            <span>{display_phone}</span>
        </a>
    </li>''')

    clean_wa = clean_phone(user['phone'])
    items.append(f'''
    <li class="contact-item">
        <a href="https://wa.me/{clean_wa}" target="_blank" class="contact-link">
            <div class="icon-box"><i class="fab fa-whatsapp"></i></div>
            <span>WhatsApp</span>
        </a>
    </li>''')

    if user.get('email'):
        items.append(f'''
        <li class="contact-item">
            <a href="mailto:{user['email']}" class="contact-link">
                <div class="icon-box"><i class="fas fa-envelope"></i></div>
                <span>{user['email']}</span>
            </a>
        </li>''')

    if user.get('website'):
        items.append(f'''
        <li class="contact-item">
            <a href="{user['website']}" target="_blank" class="contact-link">
                <div class="icon-box"><i class="fas fa-globe"></i></div>
                <span>Website</span>
            </a>
        </li>''')

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
        
        # Calculate fingerprint for this specific user's data
        # We sort keys to make sure the order doesn't mess up the hash
        user_data_string = json.dumps(user, sort_keys=True)
        user_hash = get_hash(user_data_string)
        
        # Save to new memory
        new_state['users'][user['id']] = user_hash

        # DECISION: Should we rebuild?
        # 1. Did the template change?
        # 2. Did this user's data change?
        # 3. Does the file not exist (deleted)?
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