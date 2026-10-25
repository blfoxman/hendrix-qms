# Screenshots for the manual chapter "Products, production and cultivation" (group prod)
import re, json, subprocess, copy
SCR = '/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/'
exec(open(SCR + 'mock_c.py').read())
SH = SCR + 'manual/shots/'
errors = []

# ------------------------------------------------------------------ seed data
T['hx_states'][0]['tracking_system'] = 'METRC'; T['hx_states'][1]['tracking_system'] = 'METRC'
T['hx_licenses'].append({'id': 'lic-cul', 'state_id': 'st-mo', 'name': 'Black Fox Cultivation', 'license_number': 'CUL000412', 'license_type': 'Cultivation', 'active': True, 'operation': 'cultivation'})
T['hx_licenses'][0]['operation'] = 'manufacturing'

def rm(name, qty, unit, cost=''): return {'name': name, 'qty': str(qty), 'unit': unit, 'cost_per_unit': str(cost)}
T['hx_cost_library'] = [
  {'id': 'c1', 'state_id': 'st-mo', 'category': 'raw_material', 'name': 'Distillate', 'unit': 'g', 'cost_per_unit': 1.85, 'product_types': []},
  {'id': 'c2', 'state_id': 'st-mo', 'category': 'raw_material', 'name': 'THCA isolate', 'unit': 'g', 'cost_per_unit': 1.20, 'product_types': ['pre_rolls', 'infused_flower']},
  {'id': 'c3', 'state_id': 'st-mo', 'category': 'raw_material', 'name': 'Flower (smalls)', 'unit': 'g', 'cost_per_unit': 0.80, 'product_types': ['pre_rolls', 'infused_flower', 'moon_rocks', 'snow_caps']},
  {'id': 'c4', 'state_id': 'st-mo', 'category': 'raw_material', 'name': 'Terpene blend', 'unit': 'g', 'cost_per_unit': 0.45, 'product_types': []},
  {'id': 'c5', 'state_id': 'st-mo', 'category': 'raw_material', 'name': 'Gummy base', 'unit': 'g', 'cost_per_unit': 0.02, 'product_types': ['gummies']},
  {'id': 'c6', 'state_id': 'st-mo', 'category': 'packaging', 'name': '2G AIO hardware', 'unit': 'each', 'cost_per_unit': 0.90, 'product_types': ['cartridges']},
  {'id': 'c7', 'state_id': 'st-mo', 'category': 'packaging', 'name': '1G 510 cartridge', 'unit': 'each', 'cost_per_unit': 0.55, 'product_types': ['cartridges']},
  {'id': 'c8', 'state_id': 'st-mo', 'category': 'packaging', 'name': 'Child-resistant jar', 'unit': 'each', 'cost_per_unit': 0.25, 'product_types': ['pre_rolls', 'gummies']},
  {'id': 'c9', 'state_id': 'st-mo', 'category': 'labor', 'name': 'Packaging tech', 'unit': 'hour', 'cost_per_unit': 18.00, 'product_types': []},
  {'id': 'c10', 'state_id': 'st-mo', 'category': 'labor', 'name': 'Extraction tech', 'unit': 'hour', 'cost_per_unit': 24.00, 'product_types': ['ethanol_extraction', 'butane_extraction']}]
T['hx_skus'] = [
  {'id': 'k-aio', 'state_id': 'st-mo', 'product_type': 'cartridges', 'name': 'Muha Meds 2G AIO', 'spec': {'oil_per_unit': 2}, 'license_ids': [], 'active': True, 'sort': 0},
  {'id': 'k-1g', 'state_id': 'st-mo', 'product_type': 'cartridges', 'name': 'Black Fox 1G Cartridge', 'spec': {'oil_per_unit': 1}, 'license_ids': ['lic-mo'], 'active': True, 'sort': 1},
  {'id': 'k-pod', 'state_id': 'st-mo', 'product_type': 'cartridges', 'name': 'Live Resin 0.5G Pod', 'spec': {'oil_per_unit': 0.5}, 'license_ids': [], 'active': False, 'sort': 2},
  {'id': 'k-mates', 'state_id': 'st-mo', 'product_type': 'pre_rolls', 'name': 'Mates THCA 5 x 0.6g', 'spec': {'grams_filled': 0.55, 'grams_kiefed': 0.6, 'coating': 'Kief', 'flower_type': 'Infused', 'package_name': 'Jar', 'units_per_package': 5, 'ingredients': ['THCA', 'Terpene']}, 'license_ids': [], 'active': True, 'sort': 0},
  {'id': 'k-plain', 'state_id': 'st-mo', 'product_type': 'pre_rolls', 'name': 'Black Fox 1G Plain Pre Roll', 'spec': {'grams_filled': 1.0, 'units_per_package': 1, 'no_flavor': True}, 'license_ids': [], 'active': True, 'sort': 1},
  {'id': 'k-gum', 'state_id': 'st-mo', 'product_type': 'gummies', 'name': 'Black Fox Gummies 100mg 10pk', 'spec': {'grams_per_gummy': 4.6, 'units_per_package': 10}, 'license_ids': [], 'active': True, 'sort': 0},
  {'id': 'k-bho', 'state_id': 'st-mo', 'product_type': 'butane_extraction', 'name': 'THCA / HTE', 'spec': {'dual': 'Yes'}, 'license_ids': [], 'active': True, 'sort': 0}]
FL = [('k-aio', ['Honey Melon', 'Blue Dream', 'Strawberry Lava', 'Gelato #33']), ('k-1g', ['Sour Diesel', 'Pineapple Express']), ('k-pod', ['Watermelon Zkittlez']),
      ('k-mates', ['Berry Blast', 'Honey Melon', 'Mango Haze']), ('k-gum', ['Watermelon', 'Blue Raspberry', 'Peach Ring'])]
T['hx_flavors'] = []
for sk, names in FL:
    for i, n in enumerate(names):
        T['hx_flavors'].append({'id': 'fl-%s-%d' % (sk, i), 'state_id': 'st-mo', 'sku_id': sk, 'name': n, 'active': True, 'sort': i})
def fid(sku, name): return next(f['id'] for f in T['hx_flavors'] if f['sku_id'] == sku and f['name'] == name)
T['hx_formulations'] = [
  {'id': 'fo-aio', 'state_id': 'st-mo', 'sku_id': 'k-aio', 'flavor_id': None, 'name': 'Muha Meds 2G AIO — base recipe', 'batch_size': '1000',
   'raw_materials': [rm('Distillate', 1880, 'g', 1.85), rm('Terpene blend', 120, 'g', 0.45)], 'packaging': [rm('2G AIO hardware', 1000, 'each', 0.90)], 'labor': [rm('Packaging tech', 6, 'hour', 18)], 'notes': 'Heat distillate to 60 C before mixing terpenes.'},
  {'id': 'fo-aio-bd', 'state_id': 'st-mo', 'sku_id': 'k-aio', 'flavor_id': fid('k-aio', 'Blue Dream'), 'name': 'Muha Meds 2G AIO — Blue Dream', 'batch_size': '1000',
   'raw_materials': [rm('Distillate', 1860, 'g', 1.85), rm('Terpene - Blue Dream', 140, 'g', 0.55)], 'packaging': [rm('2G AIO hardware', 1000, 'each', 0.90)], 'labor': [rm('Packaging tech', 6, 'hour', 18)], 'notes': ''},
  {'id': 'fo-1g', 'state_id': 'st-mo', 'sku_id': 'k-1g', 'flavor_id': None, 'name': 'Black Fox 1G Cartridge — base recipe', 'batch_size': '500',
   'raw_materials': [rm('Distillate', 470, 'g', 1.85), rm('Terpene blend', 30, 'g', 0.45)], 'packaging': [rm('1G 510 cartridge', 500, 'each', 0.55)], 'labor': [rm('Packaging tech', 3, 'hour', 18)], 'notes': ''},
  {'id': 'fo-mates', 'state_id': 'st-mo', 'sku_id': 'k-mates', 'flavor_id': None, 'name': 'Mates THCA — base recipe', 'batch_size': '1000',
   'raw_materials': [rm('Flower', 550, 'g', 0.80), rm('THCA', 110, 'g', 1.20), rm('Terpene', 22, 'g', 0.45)], 'packaging': [rm('Child-resistant jar', 200, 'each', 0.25)], 'labor': [rm('Packaging tech', 8, 'hour', 18)], 'notes': 'Kief coat after infusion.'},
  {'id': 'fo-mates-bb', 'state_id': 'st-mo', 'sku_id': 'k-mates', 'flavor_id': fid('k-mates', 'Berry Blast'), 'name': 'Mates THCA — Berry Blast', 'batch_size': '1000',
   'raw_materials': [rm('Flower', 550, 'g', 0.80), rm('THCA', 100, 'g', 1.20), rm('Terpene - Berry Blast', 25, 'g', 0.60)], 'packaging': [rm('Child-resistant jar', 200, 'each', 0.25)], 'labor': [], 'notes': ''},
  {'id': 'fo-plain', 'state_id': 'st-mo', 'sku_id': 'k-plain', 'flavor_id': None, 'name': 'Black Fox 1G Plain Pre Roll — base recipe', 'batch_size': '1000',
   'raw_materials': [rm('Flower (smalls)', 1020, 'g', 0.80)], 'packaging': [rm('Child-resistant jar', 1000, 'each', 0.25)], 'labor': [], 'notes': ''},
  {'id': 'fo-gum', 'state_id': 'st-mo', 'sku_id': 'k-gum', 'flavor_id': None, 'name': 'Black Fox Gummies 100mg — base recipe', 'batch_size': '1000',
   'raw_materials': [rm('Distillate', 115, 'g', 1.85), rm('Gummy base', 45885, 'g', 0.02), rm('Flavor oil', 90, 'g', 0.30)], 'packaging': [rm('Child-resistant jar', 1000, 'each', 0.25)], 'labor': [rm('Packaging tech', 10, 'hour', 18)], 'notes': ''},
  {'id': 'fo-bho', 'state_id': 'st-mo', 'sku_id': 'k-bho', 'flavor_id': None, 'name': 'THCA / HTE — base recipe', 'batch_size': '1',
   'raw_materials': [rm('Fresh frozen biomass', 10000, 'g', 0.15), rm('Butane (n-butane 99.5%)', 40, 'lb', 4.10)], 'packaging': [], 'labor': [rm('Extraction tech', 8, 'hour', 24)], 'notes': ''}]

# receiving lots (planner inventory check)
T['hx_lots'] = [
  {'id': 'l1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-088', 'item': 'Flower', 'unit': 'kg', 'quantity': 2, 'qty_used': 0.5, 'status': 'accepted', 'category': 'Cannabis'},
  {'id': 'l2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-091', 'item': 'THCA isolate', 'unit': 'g', 'quantity': 1000, 'qty_used': 120, 'status': 'accepted', 'category': 'Cannabis'},
  {'id': 'l3', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-093', 'item': 'Terpene - Berry Blast', 'unit': 'g', 'quantity': 100, 'qty_used': 10, 'status': 'accepted', 'category': 'Terpenes'},
  {'id': 'l4', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-094', 'item': 'Terpene - Mango Haze', 'unit': 'g', 'quantity': 50, 'qty_used': 0, 'status': 'accepted', 'category': 'Terpenes'},
  # cultivation license lots
  {'id': 'lt-cl', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'RCV-2026-010', 'item': 'Gelato clones', 'category': 'Clones / seeds', 'status': 'accepted', 'received_on': '2026-08-02', 'supplier_id': 's1', 'unit': 'each', 'quantity': 120, 'qty_used': 0},
  {'id': 'lt-cl2', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'RCV-2026-014', 'item': 'Blue Dream clones', 'category': 'Clones / seeds', 'status': 'accepted', 'received_on': '2026-09-12', 'supplier_id': 's1', 'unit': 'each', 'quantity': 80, 'qty_used': 0},
  {'id': 'lt-md', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'RCV-2026-011', 'item': 'Coco coir (pre-washed)', 'category': 'Grow media / soil', 'status': 'accepted', 'received_on': '2026-08-02', 'supplier_id': 's1', 'unit': 'bag', 'quantity': 40, 'qty_used': 0}]

# production plans
NOWD = '2026-10-24T14:00:00Z'
def pline(fl_name, sku, units, src, ings):
    f = next((x for x in T['hx_flavors'] if x['sku_id'] == sku and x['name'] == fl_name), None)
    return {'flavor_id': f['id'] if f else None, 'flavor': fl_name, 'units': units, 'source': src, 'recipe': '', 'ingredients': ings}
def ing(n, q, u='g'): return {'name': n, 'qty': str(q), 'unit': u}
T['hx_production_plans'] = [
  {'id': 'pp3', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'PP-2026-016', 'product_type': 'gummies', 'sku_id': 'k-gum', 'sku_name': 'Black Fox Gummies 100mg 10pk', 'planned_for': '2026-10-28', 'units_per_flavor': 1000,
   'instructions': '', 'lines': [pline('Watermelon', 'k-gum', 1000, 'base', [ing('Distillate', 115), ing('Gummy base', 45885)]), pline('Peach Ring', 'k-gum', 1000, 'base', [ing('Distillate', 115), ing('Gummy base', 45885)])],
   'grand_total': [ing('Distillate', 230), ing('Gummy base', 91770)], 'status': 'planned', 'close_note': None, 'created_by': 'Alfonso Toscano', 'created_at': '2026-10-21T15:00:00Z'},
  {'id': 'pp2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'PP-2026-015', 'product_type': 'pre_rolls', 'sku_id': 'k-mates', 'sku_name': 'Mates THCA 5 x 0.6g', 'planned_for': '2026-10-09', 'units_per_flavor': 1000,
   'instructions': '5% waste buffer', 'lines': [pline('Honey Melon', 'k-mates', 1000, 'base', [ing('Flower', 577.5), ing('THCA', 115.5), ing('Terpene - Honey Melon', 23.1)]), pline('Mango Haze', 'k-mates', 1000, 'base', [ing('Flower', 577.5), ing('THCA', 115.5), ing('Terpene - Mango Haze', 23.1)])],
   'grand_total': [ing('Flower', 1155), ing('THCA', 231)], 'status': 'in_progress', 'close_note': None, 'created_by': 'Sara Haarmann', 'created_at': '2026-10-08T13:00:00Z'},
  {'id': 'pp1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'PP-2026-014', 'product_type': 'pre_rolls', 'sku_id': 'k-mates', 'sku_name': 'Mates THCA 5 x 0.6g', 'planned_for': '2026-10-01', 'units_per_flavor': 1000,
   'instructions': '', 'lines': [pline('Berry Blast', 'k-mates', 1000, 'recipe', [ing('Flower', 550), ing('THCA', 100), ing('Terpene - Berry Blast', 25)])],
   'grand_total': [ing('Flower', 550), ing('THCA', 100), ing('Terpene - Berry Blast', 25)], 'status': 'completed', 'close_note': None, 'created_by': 'Sara Haarmann', 'created_at': '2026-09-30T13:00:00Z'},
  {'id': 'pp0', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'PP-2026-013', 'product_type': 'cartridges', 'sku_id': 'k-aio', 'sku_name': 'Muha Meds 2G AIO', 'planned_for': '2026-09-24', 'units_per_flavor': 500,
   'instructions': '', 'lines': [pline('Strawberry Lava', 'k-aio', 500, 'base', [ing('Distillate', 940), ing('Terpene - Strawberry Lava', 60)])],
   'grand_total': [ing('Distillate', 940), ing('Terpene - Strawberry Lava', 60)], 'status': 'cancelled', 'close_note': 'Hardware delivery delayed by the supplier', 'created_by': 'Sam', 'created_at': '2026-09-20T13:00:00Z'}]

# batches: raw data, recalculated in the page later with btRecalc
TAGS = {}
def tag(n): return '1A40A0300004F5B0000%05d' % n
RAW_B = [
  ('b-pr40', 'pre_rolls', 'PR-2026-040', 'k-mates', 'Honey Melon', 'In Progress', '2026-10-01', 'Amir Yrigoyen', {}, True),
  ('b-pr41', 'pre_rolls', 'PR-2026-041', 'k-mates', 'Berry Blast', 'Completed', '2026-10-02', 'Amir Yrigoyen', {
     'flower_metrc': tag(1101), 'flower_qty': '550', 'thca_metrc': tag(1102), 'thca_qty': '100', 'terp_qty': '25', 'infused_flower_number': 'IF-2026-041', 'infused_flower_total_wt': '675', 'flower_metrc_confirmed': True,
     'infused_flower_used': '550', 'infused_flower_waste': '4', 'infused_flower_waste_metrc_confirmed': True, 'total_joint_filled': '995', 'infused_preroll_metrc': tag(1103), 'joints_metrc_confirmed': True,
     'total_infused_preroll_used': '995', 'total_infused_preroll_waste': '3', 'preroll_waste_metrc_confirmed': True, 'kief_metrc': tag(1104), 'kief_qty_used': '45', 'total_kiefed_infused_joints': '912',
     'kiefed_infused_preroll_metrc': tag(1105), 'kiefed_metrc_confirmed': True, 'kiefed_infused_joints_used': '910', 'kief_infused_joints_waste': '2', 'kief_waste_metrc_confirmed': True,
     'total_jar_packaged': '182', 'final_packaged_tag': tag(1241), 'rd1_result': 'Passed', 'mandatory_testing': 'Passed', 'packaging_metrc_confirmed': True, 'notes': 'Ran on Line 2.'}, False),
  ('b-pr42', 'pre_rolls', 'PR-2026-042', 'k-mates', 'Honey Melon', 'Passed', '2026-10-09', 'Amir Yrigoyen', {
     'flower_metrc': tag(1201), 'flower_qty': '550', 'thca_metrc': tag(1202), 'thca_qty': '110', 'terp_qty': '22', 'infused_flower_number': 'IF-2026-042', 'infused_flower_total_wt': '680', 'flower_metrc_confirmed': True,
     'infused_flower_used': '550', 'total_joint_filled': '1000', 'infused_preroll_metrc': tag(1203), 'joints_metrc_confirmed': True, 'total_infused_preroll_used': '1000', 'kief_qty_used': '48',
     'total_kiefed_infused_joints': '915', 'kiefed_metrc_confirmed': True, 'kiefed_infused_joints_used': '915', 'total_jar_packaged': '183', 'final_packaged_tag': tag(1242), 'rd1_result': 'Passed', 'mandatory_testing': 'Submitted', 'packaging_metrc_confirmed': True}, False),
  ('b-pr43', 'pre_rolls', 'PR-2026-043', 'k-mates', 'Mango Haze', 'In Progress', '2026-10-20', 'Alfonso Toscano', {
     'flower_metrc': tag(1301), 'flower_qty': '550', 'thca_metrc': tag(1302), 'thca_qty': '110', 'terp_qty': '22', 'infused_flower_total_wt': '679', 'flower_metrc_confirmed': True,
     'infused_flower_used': '550', 'total_joint_filled': '1002', 'infused_preroll_metrc': tag(1303), 'joints_metrc_confirmed': True, 'total_infused_preroll_used': '1002', 'kief_qty_used': '47', 'total_kiefed_infused_joints': '918'}, False),
  ('b-pr44', 'pre_rolls', 'PR-2026-044', 'k-mates', 'Honey Melon', 'QC Hold', '2026-10-22', 'Alfonso Toscano', {
     'flower_metrc': tag(1401), 'flower_qty': '550', 'thca_metrc': tag(1402), 'thca_qty': '110', 'terp_qty': '22', 'infused_flower_total_wt': '682', 'flower_metrc_confirmed': True,
     'infused_flower_used': '550', 'total_joint_filled': '1160', 'infused_preroll_metrc': tag(1403), 'joints_metrc_confirmed': True, 'notes': 'Joint count high - QA checking fill weight.'}, False),
  ('b-ca18', 'cartridges', 'CART-2026-118', 'k-aio', 'Honey Melon', 'Completed', '2026-10-06', 'Amir Yrigoyen', {
     'oil_source_batch': 'ETH-2026-031', 'input_weight': '1880', 'terpene_added': '120', 'primed_oil_total_weight': '1996', 'primed_oil_metrc': tag(1801), 'primed_oil_used': '1990', 'primed_rd1': 'Passed',
     'cart_packaged': '992', 'cart_packaged_metrc': tag(1818), 'mandatory_test': 'Passed', 'source_metrc_confirmed': True, 'primed_metrc_confirmed': True, 'packaged_metrc_confirmed': True}, False),
  ('b-ca19', 'cartridges', 'CART-2026-119', 'k-aio', 'Blue Dream', 'QC Hold', '2026-10-13', 'Amir Yrigoyen', {
     'oil_source_batch': 'ETH-2026-031', 'input_weight': '1860', 'terpene_added': '140', 'primed_oil_total_weight': '1998', 'primed_oil_metrc': tag(1901), 'primed_oil_used': '1995',
     'cart_packaged': '994', 'cart_packaged_metrc': tag(1919), 'mandatory_test': 'Submitted', 'source_metrc_confirmed': True}, False),
  ('b-gm31', 'gummies', 'GUM-2026-031', 'k-gum', 'Watermelon', 'QC Hold', '2026-10-07', 'Alfonso Toscano', {
     'distillate_metrc': tag(3101), 'distillate_qty': '115', 'gummy_mixture_batch_weight': '46100', 'oil_source_batch': tag(3102), 'units_produced': '10010', 'gummies_batch_metrc': tag(3103),
     'total_gummies_used': '10010', 'total_gummies_waste_presugar': '20', 'sugar_coated_gummies_metrc': tag(3104), 'sugar_coated_used': '9990', 'sugar_coated_waste': '0',
     'final_packaged_gummies_metrc': tag(3131), 'gummy_mandatory_test': 'Failed'}, False),
]
T['hx_batches'] = []
for (bid, bt, num, sku, flv, status, date, who, data, void) in RAW_B:
    d = {'batch_number': num, 'date': date, 'operator': who, 'status': status, 'notes': ''}
    d.update(data)
    T['hx_batches'].append({'id': bid, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': bt, 'batch_number': num, 'sku_id': sku, 'sku': next(k['name'] for k in T['hx_skus'] if k['id'] == sku),
        'flavor_id': fid(sku, flv), 'flavor': flv, 'status': status, 'data': d, 'attachments': [], 'performed_by': who, 'signature': None, 'source': 'app',
        'created_at': date + 'T15:00:00Z', 'updated_at': date + 'T15:00:00Z', 'voided': void, 'void_reason': 'Duplicate entry - re-entered as PR-2026-042' if void else None, 'voided_at': '2026-10-09T16:00:00Z' if void else None})
T['hx_batches'].sort(key=lambda b: b['created_at'], reverse=True)

# same system-check maths as the Batch Tracker (btRecalc), so seeded batches show their checks
def n0(v):
    try: return float(str(v if v is not None else '').replace(',', ''))
    except ValueError: return 0.0
def r2(n):
    x = round(n * 100) / 100
    return str(int(x)) if x == int(x) else str(x)
def bdirect(e, a):
    if not e and not a: return 'none'
    return 'under' if a < e * 0.9 else 'over' if a > e * 1.1 else 'pass'
def bcount(e, a):
    if not e and not a: return 'none'
    return 'under' if a > e * 1.1 else 'over' if a < e * 0.9 else 'pass'
def recalc(t, f, spec):
    f = dict(f)
    if t == 'cartridges':
        s_ = n0(f.get('input_weight')) + n0(f.get('terpene_added')); f['primed_check_expected'] = r2(s_); f['primed_check_status'] = bdirect(s_, n0(f.get('primed_oil_total_weight')))
    if t == 'gummies':
        gpg = spec.get('grams_per_gummy', 4.6); per = spec.get('units_per_package', 10)
        used = n0(f.get('gummy_mixture_batch_weight')) - n0(f.get('gummy_mixture_waste')); coated = n0(f.get('units_produced')) - n0(f.get('total_gummies_waste_presugar'))
        pk = (coated - n0(f.get('sugar_coated_waste'))) / per; e = (used / gpg) / per
        f.update({'gummy_mixture_used': r2(used), 'total_sugar_coated_gummies': r2(coated), 'total_packaged_gummies': r2(pk), 'system_check_expected': r2(e), 'system_check_status': bcount(e, pk)})
    if t == 'pre_rolls':
        used = n0(f.get('infused_flower_used')); filled = spec.get('grams_filled', 0.55); kief = spec.get('grams_kiefed', 0)
        e1 = used / filled if filled else 0; e2 = used / kief if kief else 0
        s_ = sum(n0(f.get(k)) for k in ['flower_qty', 'thca_qty', 'terp_qty', 'live_resin_qty', 'hte_qty', 'decarbed_resin_qty', 'distillate_qty', 'trim_qty', 'thca_internal_qty'])
        f.update({'joints_check_expected': r2(e1), 'joints_check_status': bcount(e1, n0(f.get('total_joint_filled'))), 'kiefed_check_expected': r2(e2), 'kiefed_check_status': bcount(e2, n0(f.get('total_kiefed_infused_joints'))),
                  'flower_check_expected': r2(s_), 'flower_check_status': bdirect(s_, n0(f.get('infused_flower_total_wt')))})
        if spec.get('units_per_package'):
            src = n0(f.get('kiefed_infused_joints_used')) if kief else n0(f.get('total_joint_filled')); ep = src / spec['units_per_package']
            f['packaging_check_expected'] = r2(ep); f['packaging_check_status'] = bcount(ep, n0(f.get('total_jar_packaged')))
    return f
for bt_ in T['hx_batches']:
    sk_ = next(k for k in T['hx_skus'] if k['id'] == bt_['sku_id'])
    bt_['data'] = recalc(bt_['batch_type'], bt_['data'], sk_['spec'])
T['hx_line_clearances'] = [{'id': 'lc1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': 'b-pr41', 'number': 'LC-2026-061', 'result': 'cleared', 'checked_at': '2026-10-02T13:40:00Z', 'voided': False},
                           {'id': 'lc2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': 'b-pr42', 'number': 'LC-2026-066', 'result': 'cleared', 'checked_at': '2026-10-09T13:30:00Z', 'voided': False},
                           {'id': 'lc3', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': 'b-pr43', 'number': 'LC-2026-071', 'result': 'cleared', 'checked_at': '2026-10-20T13:10:00Z', 'voided': False}]

# tests
COA_PASS = {'lab_name': 'Green Leaf Lab', 'lab_license_number': 'TES000777', 'report_date': '2026-10-08', 'sample_metrc_tag': tag(1251), 'overall_status': 'Pass',
  'potency': {'unit': '%', 'total_thc': 41.2, 'total_cbd': 0.1, 'thca': 44.8, 'd9_thc': 1.9, 'cbn': 0.3, 'cbg': 0.9},
  'categories': {'pesticides': {'status': 'Pass', 'analytes': []}, 'microbials': {'status': 'Pass', 'analytes': []}, 'mycotoxins': {'status': 'Pass', 'analytes': []},
                 'heavy_metals': {'status': 'Pass', 'analytes': [{'name': 'Lead', 'result': '0.05', 'limit': '0.5', 'unit': 'ug/g', 'status': 'Pass'}]}, 'foreign_matter': {'status': 'Pass', 'analytes': []}, 'moisture': {'status': 'Pass', 'analytes': [{'name': 'Water activity', 'result': '0.52', 'limit': '0.65', 'unit': 'aw', 'status': 'Pass'}]}},
  'terpenes': [{'name': 'Limonene', 'value': 0.62}, {'name': 'beta-Myrcene', 'value': 0.48}, {'name': 'beta-Caryophyllene', 'value': 0.35}, {'name': 'Linalool', 'value': 0.12}], 'total_terpenes': 1.71}
COA_CART = {'lab_name': 'Green Leaf Lab', 'lab_license_number': 'TES000777', 'report_date': '2026-10-12', 'sample_metrc_tag': tag(1851), 'overall_status': 'Pass',
  'potency': {'unit': '%', 'total_thc': 88.4, 'total_cbd': 0.2, 'thca': 0.4, 'd9_thc': 88.0, 'cbn': 1.1},
  'categories': {'pesticides': {'status': 'Pass', 'analytes': []}, 'residual_solvents': {'status': 'Pass', 'analytes': [{'name': 'Ethanol', 'result': '212', 'limit': '5000', 'unit': 'ppm', 'status': 'Pass'}]}, 'heavy_metals': {'status': 'Pass', 'analytes': []}},
  'terpenes': [{'name': 'Limonene', 'value': 2.1}, {'name': 'beta-Myrcene', 'value': 1.4}], 'total_terpenes': 4.9}
COA_FAIL = {'lab_name': 'Green Leaf Lab', 'lab_license_number': 'TES000777', 'report_date': '2026-10-15', 'sample_metrc_tag': tag(3151), 'overall_status': 'Fail',
  'potency': {'unit': '%', 'total_thc': 0.22, 'd9_thc': 0.22},
  'categories': {'microbials': {'status': 'Fail', 'analytes': [{'name': 'Total yeast and mold', 'result': '15000', 'limit': '10000', 'unit': 'CFU/g', 'status': 'Fail'}]}, 'pesticides': {'status': 'Pass', 'analytes': []}}}
def test(id_, bid, tg, label, sample, status, created, result_at=None, coa=None, extra=None):
    b = next(x for x in T['hx_batches'] if x['id'] == bid)
    r = {'id': id_, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': bid, 'batch_number': b['batch_number'], 'batch_type': b['batch_type'], 'sku': b['sku'], 'flavor': b['flavor'],
         'tag': tg, 'tag_label': label, 'sample_tag': sample, 'lab_name': 'Green Leaf Lab' if status != 'Pending' else '', 'lab_license': 'TES000777' if coa else '', 'status': status,
         'submitted_at': created, 'result_at': result_at, 'result_thc': str(coa['potency']['total_thc']) if coa else '', 'result_cbd': str(coa['potency'].get('total_cbd', '')) if coa else '',
         'result_notes': '', 'notes': '', 'coa_path': 'coa/lic-mo/%s.pdf' % id_ if coa else '', 'coa_filename': ('COA_%s.pdf' % b['batch_number']) if coa else '', 'coa_analysis': coa,
         'performed_by': 'Sara Haarmann', 'voided': False, 'void_reason': None, 'created_at': created, 'retention_qty': '', 'retention_location': '', 'retention_until': None}
    if extra: r.update(extra)
    return r
T['hx_tests'] = [
  test('t-ca19', 'b-ca19', tag(1919), 'Cart Packaged', '', 'Submitted', '2026-10-14T14:00:00Z'),
  test('t-pr42', 'b-pr42', tag(1242), 'Final Packaged', tag(1252), 'Submitted', '2026-10-10T14:00:00Z'),
  test('t-gm31', 'b-gm31', tag(3131), 'Final Packaged', tag(3151), 'Failed', '2026-10-08T14:00:00Z', '2026-10-15T18:00:00Z', COA_FAIL, {'result_notes': 'Yeast and mold over the limit. Lot on hold; remediation under DEV-2026-019.'}),
  test('t-ca18', 'b-ca18', tag(1818), 'Cart Packaged', tag(1851), 'Passed', '2026-10-07T14:00:00Z', '2026-10-12T18:00:00Z', COA_CART, {'retention_qty': '2 units', 'retention_location': 'Retention cabinet B', 'retention_until': '2027-10-12'}),
  test('t-pr41', 'b-pr41', tag(1241), 'Final Packaged', tag(1251), 'Passed', '2026-10-03T14:00:00Z', '2026-10-08T18:00:00Z', COA_PASS, {'retention_qty': '1 jar (5 joints)', 'retention_location': 'Retention cabinet A', 'retention_until': '2027-10-08'}),
]
for t in T['hx_tests']:
    t['lab_name'] = t['lab_name'] or ''

# label templates
ING_PR = 'Cannabis flower, THCA isolate, kief, natural terpenes.'
T['hx_label_templates'] = [
  {'id': 'lt-bb', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'sku_id': 'k-mates', 'flavor_id': fid('k-mates', 'Berry Blast'), 'name': 'Mates THCA — Berry Blast', 'stock': 'avery-94202', 'layout': '',
   'approval_number': 'M00002721406', 'servings': '5', 'weight': '3g', 'instructions': 'Inhale. Effects may be felt within minutes and can last 2-4 hours.', 'ingredients': ING_PR + ' Terpene - Berry Blast.', 'allergens': '',
   'warning': 'For use only by adults 21 and older. Keep out of reach of children. Do not drive or operate machinery.', 'info_heading': 'MARIJUANA PRODUCT INFORMATION', 'approval_label': 'MARIJUANA PRODUCT APPROVAL NUMBER', 'results_heading': 'TEST RESULTS (mg/serving):'},
  {'id': 'lt-mates', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'sku_id': 'k-mates', 'flavor_id': None, 'name': 'Mates THCA — any flavor', 'stock': 'avery-94202', 'layout': '',
   'approval_number': 'M00002721400', 'servings': '5', 'weight': '3g', 'instructions': 'Inhale. Effects may be felt within minutes and can last 2-4 hours.', 'ingredients': ING_PR, 'allergens': '',
   'warning': 'For use only by adults 21 and older. Keep out of reach of children.', 'info_heading': 'MARIJUANA PRODUCT INFORMATION', 'approval_label': 'MARIJUANA PRODUCT APPROVAL NUMBER', 'results_heading': 'TEST RESULTS (mg/serving):'},
  {'id': 'lt-aio', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'sku_id': 'k-aio', 'flavor_id': None, 'name': 'Muha Meds 2G AIO', 'stock': 'avery-94202', 'layout': 'tri',
   'approval_number': 'M00002448284', 'servings': '200', 'weight': '2g', 'instructions': 'Inhale one puff. Wait 15 minutes before more.', 'ingredients': 'Cannabis distillate, botanical terpenes.', 'allergens': '',
   'warning': 'For use only by adults 21 and older. Keep out of reach of children.', 'info_heading': 'MARIJUANA PRODUCT INFORMATION', 'approval_label': 'MARIJUANA PRODUCT APPROVAL NUMBER', 'results_heading': 'TEST RESULTS (mg/serving):'},
  {'id': 'lt-gum', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'sku_id': 'k-gum', 'flavor_id': fid('k-gum', 'Watermelon'), 'name': 'Black Fox Gummies — Watermelon', 'stock': 'avery-94202', 'layout': '',
   'approval_number': 'M00002730115', 'servings': '10', 'weight': '46g', 'instructions': 'Eat one gummy. Effects can take up to 2 hours.', 'ingredients': 'Sugar, corn syrup, pectin, citric acid, natural flavor, cannabis distillate.', 'allergens': 'Contains: coconut oil (tree nut).',
   'warning': 'For use only by adults 21 and older. Keep out of reach of children.', 'info_heading': 'MARIJUANA PRODUCT INFORMATION', 'approval_label': 'MARIJUANA PRODUCT APPROVAL NUMBER', 'results_heading': 'TEST RESULTS (mg/serving):'},
  {'id': 'lt-1g', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'sku_id': 'k-1g', 'flavor_id': None, 'name': 'Black Fox 1G Cartridge', 'stock': 'avery-94202', 'layout': '',
   'approval_number': '', 'servings': '100', 'weight': '1g', 'instructions': 'Inhale one puff.', 'ingredients': '', 'allergens': '', 'warning': 'Keep out of reach of children.',
   'info_heading': 'MARIJUANA PRODUCT INFORMATION', 'approval_label': 'MARIJUANA PRODUCT APPROVAL NUMBER', 'results_heading': 'TEST RESULTS (mg/serving):'}]
T['hx_label_prints'] = [{'id': 'lp1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'test_id': 't-pr41', 'template_id': 'lt-bb', 'batch_number': 'PR-2026-041', 'tag': tag(1241), 'sku': 'Mates THCA 5 x 0.6g', 'flavor': 'Berry Blast',
   'count': 200, 'start_pos': 1, 'printed_by': 'Sara Haarmann', 'created_at': '2026-10-09T15:20:00Z'}]

# cultivation
T['hx_chemicals'] = [
  {'id': 'ch-n', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'CHEM-004', 'name': 'Bloom A+B nutrient', 'manufacturer': 'General Hydroponics', 'purpose': 'Nutrient / fertilizer', 'grade': 'non_food', 'status': 'approved', 'sds_files': [{'path': 'x', 'name': 'bloom_sds.pdf'}], 'storage_area': 'Nutrient room', 'epa_reg': ''},
  {'id': 'ch-c', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'CHEM-005', 'name': 'Cal-Mag supplement', 'manufacturer': 'Botanicare', 'purpose': 'Nutrient / fertilizer', 'grade': 'non_food', 'status': 'approved', 'sds_files': [{'path': 'y', 'name': 'calmag_sds.pdf'}], 'storage_area': 'Nutrient room', 'epa_reg': ''},
  {'id': 'ch-p', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'CHEM-007', 'name': 'Neem oil 70%', 'manufacturer': 'Monterey', 'purpose': 'Pesticide / crop protection', 'grade': 'non_food', 'status': 'approved', 'sds_files': [{'path': 'z', 'name': 'neem_sds.pdf'}], 'storage_area': 'Pesticide cabinet', 'epa_reg': '70051-2'},
  {'id': 'ch-p2', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'CHEM-008', 'name': 'Bacillus thuringiensis (Bt)', 'manufacturer': 'Bonide', 'purpose': 'Pesticide / crop protection', 'grade': 'non_food', 'status': 'approved', 'sds_files': [{'path': 'w', 'name': 'bt_sds.pdf'}], 'storage_area': 'Pesticide cabinet', 'epa_reg': '73049-39'}]
T['hx_grow_areas'] = [
  {'id': 'ga1', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'name': 'Flower Room 1', 'kind': 'indoor', 'canopy_sqft': 1200, 'irrigation': 'Drip fertigation', 'water_source': 'City water through RO', 'limits': '68-80 F, 40-60% RH', 'land_use': '', 'risk_assessed_on': None, 'risk_notes': '', 'active': True, 'sort': 0},
  {'id': 'ga2', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'name': 'Flower Room 2', 'kind': 'indoor', 'canopy_sqft': 1200, 'irrigation': 'Drip fertigation', 'water_source': 'City water through RO', 'limits': '68-80 F, 40-60% RH', 'land_use': '', 'risk_assessed_on': None, 'risk_notes': '', 'active': True, 'sort': 1},
  {'id': 'ga3', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'name': 'Veg Room', 'kind': 'indoor', 'canopy_sqft': 600, 'irrigation': 'Hand watering', 'water_source': 'City water through RO', 'limits': '72-82 F, 55-70% RH', 'land_use': '', 'risk_assessed_on': None, 'risk_notes': '', 'active': True, 'sort': 2},
  {'id': 'ga4', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'name': 'Mother Room', 'kind': 'mother', 'canopy_sqft': 200, 'irrigation': 'Hand watering', 'water_source': 'City water through RO', 'limits': '72-80 F, 50-65% RH', 'land_use': '', 'risk_assessed_on': None, 'risk_notes': '', 'active': True, 'sort': 3},
  {'id': 'ga5', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'name': 'Greenhouse A', 'kind': 'greenhouse', 'canopy_sqft': 3000, 'irrigation': 'Drip', 'water_source': 'Well, tested yearly', 'limits': '60-85 F', 'land_use': 'Former hay field; neighbor grows soybeans', 'risk_assessed_on': '2026-03-10', 'risk_notes': 'Fenced; buffer strip to the soybean field; portable handwashing station.', 'active': True, 'sort': 4},
  {'id': 'ga6', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'name': 'Dry Room', 'kind': 'dry', 'canopy_sqft': None, 'irrigation': '', 'water_source': '', 'limits': '60 F, 60% RH', 'land_use': '', 'risk_assessed_on': None, 'risk_notes': '', 'active': True, 'sort': 5},
  {'id': 'ga7', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'name': 'Cure Room', 'kind': 'cure', 'canopy_sqft': None, 'irrigation': '', 'water_source': '', 'limits': '62 F, 58-62% RH', 'land_use': '', 'risk_assessed_on': None, 'risk_notes': '', 'active': True, 'sort': 6}]
def pbatch(id_, num, cult, n, stage, area, planted, src_lot=None, mother=None, extra=None):
    r = {'id': id_, 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': num, 'cultivar': cult, 'plant_count': n, 'stage': stage, 'area_id': area, 'planted_on': planted,
         'source_kind': 'lot' if src_lot else 'mother', 'source_lot_id': src_lot, 'mother_batch_id': mother, 'source_note': '', 'media_lot_id': 'lt-md', 'media': 'New coco, pre-washed',
         'metrc_tag': '1A40A0300004F5C00000%04d' % int(num[-3:]), 'notes': '', 'harvest_after': None, 'wet_weight': None, 'dry_weight': None, 'harvest_tag': '', 'created_at': planted + 'T12:00:00Z', 'created_by': 'Sam'}
    if extra: r.update(extra)
    return r
T['hx_plant_batches'] = [
  pbatch('pb24', 'PB-2026-024', 'Gelato', 40, 'propagation', 'ga3', '2026-10-19', mother='pb20'),
  pbatch('pb22', 'PB-2026-022', 'Blue Dream', 60, 'vegetative', 'ga3', '2026-09-14', src_lot='lt-cl2'),
  pbatch('pb21', 'PB-2026-021', 'Gelato', 48, 'flowering', 'ga1', '2026-08-04', src_lot='lt-cl', extra={'harvest_after': '2026-10-30'}),
  pbatch('pb20', 'PB-2026-020', 'Gelato (mothers)', 6, 'vegetative', 'ga4', '2026-08-04', src_lot='lt-cl'),
  pbatch('pb19', 'PB-2026-019', 'Wedding Cake', 50, 'drying', 'ga6', '2026-07-01', src_lot='lt-cl', extra={'wet_weight': 14200, 'harvest_tag': '1A40A0300004F5D00000019'}),
  pbatch('pb17', 'PB-2026-017', 'Sour Diesel', 45, 'done', 'ga7', '2026-06-02', src_lot='lt-cl', extra={'wet_weight': 12600, 'dry_weight': 2780, 'harvest_tag': '1A40A0300004F5D00000017'})]
def gev(id_, bid, kind, on, by, **kw):
    r = {'id': id_, 'state_id': 'st-mo', 'license_id': 'lic-cul', 'batch_id': bid, 'kind': kind, 'done_on': on, 'done_by': by, 'area_id': None, 'chemical_id': None, 'lot_id': None, 'product': '', 'epa_reg': '',
         'amount': '', 'method': '', 'rei_hours': None, 'phi_days': None, 'stage': '', 'observations': '', 'wet_weight': None, 'dry_weight': None, 'waste_weight': None, 'tag': '', 'conditions': '', 'files': [],
         'recorded_by': by, 'voided': False, 'void_reason': None, 'created_at': on + 'T16:00:00Z'}
    r.update(kw); return r
T['hx_grow_events'] = [
  gev('e9', 'pb21', 'crop_protection', '2026-10-16', 'Amir Yrigoyen', chemical_id='ch-p', product='Neem oil 70%', epa_reg='70051-2', amount='1 oz/gal', method='Foliar spray', rei_hours=4, phi_days=14, observations='Spider mites, lower canopy'),
  gev('e8', 'pb21', 'scouting', '2026-10-15', 'Amir Yrigoyen', observations='Spider mite stippling on lower leaves, rows 3-5. Recommend treatment.'),
  gev('e7', 'pb21', 'input', '2026-10-14', 'Amir Yrigoyen', chemical_id='ch-n', product='Bloom A+B nutrient', amount='2 mL/L', method='Drip fertigation'),
  gev('e10', 'pb22', 'input', '2026-10-21', 'Amir Yrigoyen', chemical_id='ch-c', product='Cal-Mag supplement', amount='1 mL/L', method='Hand watering'),
  gev('e6', 'pb21', 'crop_protection', '2026-10-02', 'Amir Yrigoyen', chemical_id='ch-p2', product='Bacillus thuringiensis (Bt)', epa_reg='73049-39', amount='2 tsp/gal', method='Foliar spray', rei_hours=4, phi_days=0, voided=True, void_reason='Entered on the wrong batch', observations='Caterpillars'),
  gev('e5', 'pb21', 'stage', '2026-09-08', 'Amir Yrigoyen', stage='flowering', area_id='ga1'),
  gev('e4', 'pb19', 'harvest', '2026-10-18', 'Amir Yrigoyen', wet_weight=14200, waste_weight=650, tag='1A40A0300004F5D00000019', area_id='ga6'),
  gev('e3', 'pb21', 'input', '2026-08-20', 'Amir Yrigoyen', chemical_id='ch-n', product='Bloom A+B nutrient', amount='1.5 mL/L', method='Drip fertigation')]

# ------------------------------------------------------------------ extra endpoints
_h = handle
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
PSEQ = [17]
def handle(route, request):
    u = request.url; m = request.method; path = urllib.parse.urlparse(u).path; tbl = path.split('/')[-1]
    if path.endswith('/rpc/hx_planner_recipes'):
        sk = json.loads(request.post_data)['p_sku']
        return jr(route, [{'flavor_id': f['flavor_id'], 'name': f['name'], 'batch_size': f['batch_size'], 'raw_materials': [{'name': r['name'], 'qty': r['qty'], 'unit': r['unit'] or 'g'} for r in f['raw_materials']]} for f in T['hx_formulations'] if f['sku_id'] == sk])
    if tbl == 'hx_production_plans' and m == 'POST':
        r = json.loads(request.post_data); r.update({'number': 'PP-2026-%03d' % PSEQ[0], 'status': 'planned', 'created_by': 'Sam', 'created_at': NOWD}); PSEQ[0] += 1
        T['hx_production_plans'].insert(0, r); return jr(route, [r], 201)
    return _h(route, request)

def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first

def modal_shot(pg, name, max_h=2400, clip_to=None):
    """Element shot of the whole modal (no inner scroll). clip_to: a locator whose top ends the shot."""
    pg.evaluate("()=>{const m=document.querySelector('.md');m.style.maxHeight='none';m.parentElement.style.alignItems='flex-start';m.parentElement.style.overflow='auto';}")
    h = pg.evaluate("()=>document.querySelector('.md').scrollHeight")
    vp = pg.viewport_size
    pg.set_viewport_size({'width': vp['width'], 'height': min(max(900, h + 60), max_h)})
    pg.wait_for_timeout(250)
    box = pg.locator('.md').bounding_box()
    if clip_to is not None:
        cb = clip_to.bounding_box()
        pg.screenshot(path=SH + name, clip={'x': box['x'], 'y': box['y'], 'width': box['width'], 'height': min(cb['y'] - box['y'], max_h - 20)})
    elif box['height'] > max_h - 40:
        pg.screenshot(path=SH + name, clip={'x': box['x'], 'y': box['y'], 'width': box['width'], 'height': max_h - 40})
    else:
        pg.locator('.md').screenshot(path=SH + name)
    pg.set_viewport_size(vp)
    pg.evaluate("()=>{const m=document.querySelector('.md');if(m){m.style.maxHeight='';m.parentElement.style.alignItems='';m.parentElement.style.overflow='';}}")

def close_modal(pg):
    if pg.locator('.mo').count():
        pg.locator('.mo').first.click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(250)

def nav(pg, name):
    close_modal(pg)
    pg.get_by_role('button', name=name, exact=True).first.click(); pg.wait_for_timeout(500)
    pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(150)

shots = []
def S(pg, name):
    pg.screenshot(path=SH + name); shots.append(name)

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell')
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1.5, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('if(!sessionStorage.getItem("seeded")){sessionStorage.setItem("seeded","1");localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");localStorage.setItem("hx_ptype","cartridges");localStorage.setItem("hx_btype","pre_rolls");localStorage.setItem("hx_pptype","pre_rolls");localStorage.setItem("hx_cultab","batches");}' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')


    # =============================== PRODUCTS
    nav(pg, 'Products'); pg.wait_for_selector('.card >> text=Muha Meds 2G AIO')
    pg.evaluate('window.scrollTo(0,0)'); S(pg, 'prod_products_skus.png')
    # wizard on Gummies
    pg.locator('.tabs button', has_text='Gummies').click(); pg.wait_for_selector('.card >> text=Black Fox Gummies 100mg 10pk')
    pg.get_by_role('button', name='+ New SKU').click(); md = pg.locator('.md')
    field(md, 'SKU name').fill('Black Fox Gummies 200mg 20pk'); field(md, 'Grams per gummy').fill('4.6'); field(md, 'Gummies per package').fill('20')
    field(md, 'Flavors - one per line').fill('Watermelon\nBlue Raspberry\nPeach Ring\nSour Apple')
    modal_shot(pg, 'prod_products_wizard1.png'); shots.append('prod_products_wizard1.png')
    md.get_by_role('button', name='Next: formulation').click()
    field(md, 'Standard batch size').fill('1000')
    sel = md.locator('select', has=pg.locator('option', has_text='+ Add from price library')).first
    sel.select_option(label='Distillate ($1.85/g)'); md.locator('.li').nth(0).locator('input').nth(1).fill('230')
    sel = md.locator('select', has=pg.locator('option', has_text='+ Add from price library')).first
    sel.select_option(label='Gummy base ($0.02/g)'); md.locator('.li').nth(1).locator('input').nth(1).fill('91770')
    md.get_by_role('button', name='+ Add Material').click(); li = md.locator('.li').nth(2); li.locator('input').nth(0).fill('Flavor oil'); li.locator('input').nth(1).fill('180'); li.locator('input').nth(2).fill('g'); li.locator('input').nth(3).fill('0.30')
    sel = md.locator('select', has=pg.locator('option', has_text='+ Add from price library')).nth(1)
    sel.select_option(label='Child-resistant jar ($0.25/each)'); md.locator('.li').nth(3).locator('input').nth(1).fill('1000')
    sel = md.locator('select', has=pg.locator('option', has_text='+ Add from price library')).nth(2)
    sel.select_option(label='Packaging tech ($18.00/hour)'); md.locator('.li').nth(4).locator('input').nth(1).fill('12')
    modal_shot(pg, 'prod_products_wizard2.png'); shots.append('prod_products_wizard2.png')
    md.get_by_role('button', name='Back').click(); md.get_by_role('button', name='Cancel').click(); pg.wait_for_timeout(300)
    # formulation bank
    pg.locator('.tabs button', has_text='Formulation Bank').click(); pg.wait_for_selector('text=8 formulations')
    S(pg, 'prod_products_bank.png')
    # prices
    pg.locator('.tabs button', has_text='Ingredient Prices').click(); pg.wait_for_selector('td >> text=Distillate')
    field(pg, 'Name').fill('Kief'); field(pg, 'Unit').fill('g'); field(pg, 'Cost / unit').fill('2.40')
    pg.locator('label.ck', has_text='Pre-Rolls').locator('input').check()
    S(pg, 'prod_products_prices.png')

    # =============================== PRODUCTION PLANNER
    nav(pg, 'Production Planner'); pg.wait_for_selector('text=Calculate ingredients')
    field(pg, 'Product type').select_option('pre_rolls'); field(pg, 'SKU').select_option('k-mates')
    pg.get_by_role('link', name='Select all').click(); pg.wait_for_selector('text=Exact amounts from saved formulations')
    field(pg, 'Units per flavor').fill('1000'); field(pg, 'Planned for').fill('2026-10-29'); field(pg, 'Additional instructions (optional)').fill('5% waste buffer')
    pg.get_by_role('button', name='Calculate ingredients').click(); pg.wait_for_selector('text=Grand total')
    pg.mouse.move(5, 5)
    S(pg, 'prod_planner_calc.png')
    pg.evaluate("()=>{const c=[...document.querySelectorAll('.card.gold')].find(x=>x.textContent.includes('Grand total'));window.scrollTo(0,c.getBoundingClientRect().top+window.scrollY-170);}"); pg.wait_for_timeout(200)
    S(pg, 'prod_planner_results.png')
    pg.get_by_role('button', name='Save plan').click(); pg.wait_for_selector('text=← All plans')
    pg.get_by_role('button', name='← All plans').click(); pg.wait_for_selector('td >> text=PP-2026-017'); pg.evaluate('window.scrollTo(0,0)')
    S(pg, 'prod_planner_plans.png')
    pg.locator('tr', has_text='PP-2026-016').get_by_role('button', name='Open').click(); pg.get_by_role('button', name='Cancel plan').click()
    pg.locator('.md textarea').fill('Dispensary order moved to November.')
    pg.locator('.md').screenshot(path=SH + 'prod_planner_cancel.png'); shots.append('prod_planner_cancel.png')
    pg.locator('.md').get_by_role('button', name='Back').click()

    # =============================== BATCH TRACKER
    nav(pg, 'Batch Tracker'); pg.wait_for_selector('.card >> text=PR-2026-041')
    S(pg, 'prod_batches_list.png')
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    field(md, 'SKU').select_option(label='Mates THCA 5 x 0.6g'); field(md, 'Flavor').select_option(label='Berry Blast')
    field(md, 'Batch / Lot Number').fill('PR-2026-045')
    field(md, 'Flower METRC #').fill(tag(4501)); field(md, 'Flower Used').fill('550'); field(md, 'THCA #').fill(tag(4502)); field(md, 'THCA Used').fill('100'); field(md, 'Terpene Used').fill('25')
    field(md, 'Infused Flower #').fill('IF-2026-045'); field(md, 'Infused Flower Total WT').fill('674')
    field(md, 'Infused Flower Used').fill('550'); field(md, 'Total Joint Filled').fill('998')
    field(md, 'Kief QTY Used').fill('46'); field(md, 'Total Kiefed Infused Joints').fill('915'); field(md, 'Kiefed Infused Joints Used').fill('912'); field(md, 'Total Jar Packaged').fill('182')
    md.locator('label.ck', has_text='Recorded on METRC?').nth(0).locator('input').check(); md.locator('label.ck', has_text='Recorded on METRC?').nth(1).locator('input').check()
    md.locator('div.f', has=pg.locator('span', has_text='R&D 1')).get_by_role('button', name='Passed').click()
    modal_shot(pg, 'prod_batches_form.png', max_h=2000); shots.append('prod_batches_form.png')
    pg.locator('.md').evaluate('m=>m.scrollTo(0, m.scrollHeight)'); pg.wait_for_timeout(200)
    pg.locator('.md').screenshot(path=SH + 'prod_batches_form_end.png'); shots.append('prod_batches_form_end.png')
    md.get_by_role('button', name='Cancel').click(); pg.wait_for_timeout(200)
    # admin edit with reason -> history
    pg.locator('.card', has_text='PR-2026-042').get_by_role('button', name='Edit', exact=True).click(); pg.wait_for_selector('.md >> text=Reason for change')
    md = pg.locator('.md'); field(md, 'Total Joint Filled').fill('1004'); field(md, 'Reason for change').fill('Recount at end of shift (QA Sara H.)')
    md.get_by_role('button', name='Save changes').click(); pg.wait_for_selector('.md', state='detached')
    pg.locator('.card', has_text='PR-2026-042').get_by_role('button', name='View', exact=True).click(); pg.wait_for_selector('.md .hxrec')
    pg.locator('.md').evaluate('m=>m.scrollTo(0, m.scrollHeight)'); pg.wait_for_timeout(200)
    pg.locator('.md').screenshot(path=SH + 'prod_batches_view.png'); shots.append('prod_batches_view.png')
    pg.locator('.md').get_by_role('button', name='Close').click()

    # =============================== TESTING
    nav(pg, 'Testing'); pg.wait_for_selector('.card >> text=PR-2026-041')
    S(pg, 'prod_testing_list.png')
    pg.locator('.card', has_text='PR-2026-041').get_by_role('button', name='Show analysis').click(); pg.wait_for_selector('.barrow >> text=Total THC')
    pg.evaluate("()=>{const c=[...document.querySelectorAll('.card')].find(x=>x.textContent.startsWith('PR-2026-041'));window.scrollTo(0,c.getBoundingClientRect().top+window.scrollY-110);}"); pg.wait_for_timeout(200)
    S(pg, 'prod_testing_analysis.png')
    pg.evaluate('window.scrollTo(0,0)')
    pg.get_by_role('button', name='+ New test record').click(); md = pg.locator('.md'); pg.wait_for_selector('.md option >> text=PR-2026-043', state='attached')
    field(md, 'Batch').select_option('b-pr44'); field(md, 'Package tag tested').fill(tag(1444)); field(md, 'Sample tag').fill(tag(1454)); field(md, 'Lab').fill('Green Leaf Lab')
    field(md, 'Status').select_option('Submitted'); field(md, 'Notes').fill('Resample requested by QA after fill-weight check.')
    md.screenshot(path=SH + 'prod_testing_new.png'); shots.append('prod_testing_new.png')
    md.get_by_role('button', name='Cancel').click()
    pg.locator('.card', has_text='CART-2026-118').get_by_role('button', name='Update').click(); md = pg.locator('.md')
    field(md, 'Status').select_option('Retest'); field(md, 'Reason for changing').fill('Lab reported a calibration error on the potency run; resample requested.')
    modal_shot(pg, 'prod_testing_update.png'); shots.append('prod_testing_update.png')
    md.get_by_role('button', name='Cancel').click()

    # =============================== COMPLIANCE STICKERS
    nav(pg, 'Compliance Stickers'); pg.wait_for_selector('.card >> text=Black Fox Gummies — Watermelon')
    S(pg, 'prod_stickers_templates.png')
    pg.locator('.card', has_text='Black Fox Gummies — Watermelon').get_by_role('button', name='Edit').click(); pg.wait_for_selector('.md >> text=Allergen declaration')
    modal_shot(pg, 'prod_stickers_editor.png', clip_to=pg.locator('.md .k', has_text='Preview with sample results')); shots.append('prod_stickers_editor.png')
    pg.locator('.md').get_by_role('button', name='Cancel').click()
    nav(pg, 'Testing'); pg.wait_for_selector('.card >> text=PR-2026-041')
    pg.locator('.card', has_text='PR-2026-041').get_by_role('button', name='Compliance Sticker').click(); pg.wait_for_selector('.md iframe')
    md = pg.locator('.md'); field(md, 'Labels to print').fill('40')
    with pg.expect_download() as di: md.get_by_role('button', name='Download PDF').click()
    di.value.save_as(SCR + 'manual/_labels_prod.pdf')
    pg.wait_for_selector('text=2 prints')
    modal_shot(pg, 'prod_stickers_print.png', clip_to=md.locator('iframe')); shots.append('prod_stickers_print.png')
    close_modal(pg)

    # =============================== CULTIVATION
    close_modal(pg)
    pg.locator('select').nth(1).select_option('lic-cul'); pg.wait_for_timeout(700)
    nav(pg, 'Cultivation'); pg.wait_for_selector('td >> text=PB-2026-021')
    S(pg, 'prod_cultivation_batches.png')
    pg.locator('tr', has_text='PB-2026-021').get_by_role('button', name='Open').click(); pg.wait_for_selector('.md >> text=Pre-harvest interval running')
    pg.locator('.md').screenshot(path=SH + 'prod_cultivation_batch.png'); shots.append('prod_cultivation_batch.png')
    pg.locator('.md').get_by_role('button', name='Crop protection').click(); md = pg.locator('.md').last
    field(md, 'Approved pesticide (Chemicals) *').select_option('ch-p'); field(md, 'Rate (label) *').fill('1 oz/gal'); field(md, 'Method').fill('Foliar spray')
    field(md, 'Re-entry (hours) *').fill('4'); field(md, 'Pre-harvest (days) *').fill('14'); field(md, 'Target pest / disease').fill('Spider mites, follow-up spray')
    md.screenshot(path=SH + 'prod_cultivation_crop.png'); shots.append('prod_cultivation_crop.png')
    md.get_by_role('button', name='Cancel').click(); pg.wait_for_timeout(200)
    pg.locator('.md').first.get_by_role('button', name='Harvest').click(); md = pg.locator('.md').last
    field(md, 'Wet weight (g) *').fill('13800'); field(md, 'Harvest batch tag (METRC) *').fill('1A40A0300004F5D00000021')
    md.screenshot(path=SH + 'prod_cultivation_harvest.png'); shots.append('prod_cultivation_harvest.png')
    md.get_by_role('button', name='Cancel').click(); pg.wait_for_timeout(200)
    close_modal(pg)
    pg.locator('.tabs button', has_text='Grow areas').click(); pg.wait_for_selector('td >> text=Greenhouse A')
    S(pg, 'prod_cultivation_areas.png')
    b.close()

# sticker sheet: render the downloaded PDF and crop the top rows
subprocess.run(['pdftoppm', '-r', '220', '-f', '1', '-l', '1', '-png', SCR + 'manual/_labels_prod.pdf', SCR + 'manual/_labels_prod'], check=True)
from PIL import Image
import glob
src = sorted(glob.glob(SCR + 'manual/_labels_prod*.png'))[0]
im = Image.open(src); W, H = im.size
im.crop((int(W * 0.005), int(H * 0.04), int(W * 0.51), int(H * 0.235))).save(SH + 'prod_stickers_sheet.png'); shots.append('prod_stickers_sheet.png')
print('shots:', len(shots)); print('\n'.join(shots))
print('JS errors:', errors if errors else 'none')
