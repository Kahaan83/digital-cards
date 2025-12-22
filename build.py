import json
import os
import re
import urllib.parse
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'public')
PHOTOS_DIR = os.path.join(BASE_DIR, 'photos')

def clean_phone(phone):
    return re.sub(r'[^0-9]', '', phone)

def find_image(filename, dest):
    if not filename: return None
    if filename.startswith('http'): return filename
    
    # Try exact match
    src = os.path.join(PHOTOS_DIR, filename)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(dest, filename))
        return filename
        
    # Try extensions
    name = os.path.splitext(filename)[0]
    for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']:
        if os.path.exists(os.path.join(PHOTOS_DIR, name + ext)):
            shutil.copy(os.path.join(PHOTOS_DIR, name + ext), os.path.join(dest, name + ext))
            return name + ext
    return None

def generate_socials(user):
    # Generates icons only if links exist
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
    # Generates the list items (Phone, Email, Loc) in Python to avoid HTML errors
    items = []
    
    # Phone (Formatted with space)
    display_phone = user['phone'].replace('+91', '+91 ')
    items.append(f'''
    <li class="contact-item">
        <a href="tel:{user['phone']}" class="contact-link">
            <div class="icon-box"><i class="fas fa-phone"></i></div>
            <span>{display_phone}</span>
        </a>
    </li>''')
    # WhatsApp
    clean_wa = clean_phone(user['phone'])
    items.append(f'''
    <li class="contact-item">
        <a href="https://wa.me/{clean_wa}" target="_blank" class="contact-link">
            <div class="icon-box"><i class="fab fa-whatsapp"></i></div>
            <span>WhatsApp</span>
        </a>
    </li>''')

    # Email (Conditional)
    if user.get('email'):
        items.append(f'''
        <li class="contact-item">
            <a href="mailto:{user['email']}" class="contact-link">
                <div class="icon-box"><i class="fas fa-envelope"></i></div>
                <span>{user['email']}</span>
            </a>
        </li>''')

    # Website (Conditional)
    if user.get('website'):
        items.append(f'''
        <li class="contact-item">
            <a href="{user['website']}" target="_blank" class="contact-link">
                <div class="icon-box"><i class="fas fa-globe"></i></div>
                <span>Website</span>
            </a>
        </li>''')

    # Location (Smart Logic: Link vs Text)
    if user.get('location_text'):
        text = user['location_text']
        url = user.get('location_url')
        
        if url:
            # It's a link
            items.append(f'''
            <li class="contact-item">
                <a href="{url}" target="_blank" class="contact-link">
                    <div class="icon-box"><i class="fas fa-map-marker-alt"></i></div>
                    <span>{text}</span>
                </a>
            </li>''')
        else:
            # It's just text
            items.append(f'''
            <li class="contact-item">
                <div class="contact-link">
                    <div class="icon-box"><i class="fas fa-map-marker-alt"></i></div>
                    <span>{text}</span>
                </div>
            </li>''')

    return "".join(items)

def main():
    with open(os.path.join(BASE_DIR, 'data.json'), 'r', encoding='utf-8') as f: users = json.load(f)
    with open(os.path.join(BASE_DIR, 'template.html'), 'r', encoding='utf-8') as f: template = f.read()

    if os.path.exists(OUTPUT_DIR): shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    for user in users:
        u_dir = os.path.join(OUTPUT_DIR, user['id'])
        os.makedirs(u_dir)

        # Images
        photo = find_image(user['photo_url'], u_dir)
        banner = find_image(user.get('banner_url'), u_dir)
        
        # Banner CSS
        if banner:
            banner_css = f"background-image: url('{banner}'); background-size: cover; background-position: center;"
        else:
            banner_css = f"background: linear-gradient(135deg, {user.get('theme_color', '#333')}, #444);"

        # Buttons
        loc_btn = ""
        if user.get('location_url'):
            loc_btn = f'''<a href="{user['location_url']}" target="_blank" class="btn btn-outline"><i class="fas fa-map-marker-alt" style="color:#db4437"></i> Direction</a>'''
        
        pay_btn = ""
        if user.get('upi_id'):
            pay_link = f"upi://pay?pa={user['upi_id']}&pn={urllib.parse.quote(user['name'])}&cu=INR"
            pay_btn = f'''<a href="{pay_link}" class="btn btn-payment"><i class="fab fa-google-pay" style="color:#4285F4"></i> Pay</a>'''

        # Generate HTML sections
        contact_html = generate_contact_list(user)
        social_html = generate_socials(user)

        # Replace in Template
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
            '{{ contact_list }}': contact_html,   # <--- The magic fix
            '{{ social_section }}': social_html
        }

        for k, v in replacements.items():
            content = content.replace(k, str(v))

        with open(os.path.join(u_dir, 'index.html'), 'w', encoding='utf-8') as f: f.write(content)
        
        # VCard
        vcard = f"BEGIN:VCARD\nVERSION:3.0\nFN:{user['name']}\nTEL:{user['phone']}\nEND:VCARD"
        with open(os.path.join(u_dir, 'contact.vcf'), 'w', encoding='utf-8') as f: f.write(vcard)

        print(f"✅ Built {user['name']}")

if __name__ == "__main__":
    main()