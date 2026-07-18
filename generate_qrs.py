import os
import qrcode

# 1. Create the required Gazebo folders
os.makedirs('src/delivery_core/materials/textures', exist_ok=True)
os.makedirs('src/delivery_core/materials/scripts', exist_ok=True)

# 2. Generate the QR Images
items = ['Wheels', 'Engine', 'Shampoo', 'Laptop']
for item in items:
    img = qrcode.make(item)
    img.save(f'src/delivery_core/materials/textures/{item.lower()}.png')

# 3. Create the Gazebo Material Linker File
material_content = ""
for item in items:
    material_content += f"""
material QR/{item}
{{
  technique
  {{
    pass
    {{
      texture_unit
      {{
        texture {item.lower()}.png
      }}
    }}
  }}
}}
"""
with open('src/delivery_core/materials/scripts/qr_codes.material', 'w') as f:
    f.write(material_content)

print("SUCCESS! QR Textures and Gazebo Materials Generated.")
