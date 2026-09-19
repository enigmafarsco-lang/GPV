"""Train with YOUR labeled feature table; this example does not fabricate physical material labels."""
from gpr_workstation.classification import train_from_csv
train_from_csv('labeled_target_features.csv','site_material_model.pkl',label_column='label')
