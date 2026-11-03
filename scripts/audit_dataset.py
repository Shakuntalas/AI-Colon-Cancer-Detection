import os
import hashlib
from collections import defaultdict
import numpy as np
import tensorflow as tf

def audit_dataset():
    data_dir = os.path.expanduser(
        '~/.cache/kagglehub/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images/versions/1/lung_colon_image_set/colon_image_sets'
    )
    
    print(f"[*] Auditing dataset at: {data_dir}")
    
    # 1. Intra-class duplicates
    class_stats = {}
    for cls in ['colon_aca', 'colon_n']:
        folder = os.path.join(data_dir, cls)
        files = sorted(os.listdir(folder))
        hashes = defaultdict(list)
        for f in files:
            path = os.path.join(folder, f)
            h = hashlib.md5(open(path, 'rb').read()).hexdigest()
            hashes[h].append(f)
            
        dup_groups = {h: flist for h, flist in hashes.items() if len(flist) > 1}
        num_dup_files = sum(len(flist) - 1 for flist in dup_groups.values())
        class_stats[cls] = {
            'total_files': len(files),
            'unique_hashes': len(hashes),
            'dup_groups': len(dup_groups),
            'redundant_files': num_dup_files,
            'dup_examples': list(dup_groups.items())[:3]
        }
        print(f"[{cls}] Total: {len(files)}, Unique: {len(hashes)}, Duplicate Groups: {len(dup_groups)}, Redundant duplicates: {num_dup_files}")

    # 2. Cross-class duplicates
    all_hashes = defaultdict(dict)
    for cls in ['colon_aca', 'colon_n']:
        folder = os.path.join(data_dir, cls)
        for f in sorted(os.listdir(folder)):
            path = os.path.join(folder, f)
            h = hashlib.md5(open(path, 'rb').read()).hexdigest()
            all_hashes[h][cls] = f

    cross_duplicates = [h for h, cl_dict in all_hashes.items() if len(cl_dict) > 1]
    print(f"[*] Cross-class duplicates between colon_aca and colon_n: {len(cross_duplicates)}")

    # 3. Train vs Validation split overlap
    datagen = tf.keras.preprocessing.image.ImageDataGenerator(validation_split=0.2)
    train_gen = datagen.flow_from_directory(
        data_dir, subset='training', classes=['colon_aca', 'colon_n'], shuffle=False
    )
    val_gen = datagen.flow_from_directory(
        data_dir, subset='validation', classes=['colon_aca', 'colon_n'], shuffle=False
    )

    train_names = set(train_gen.filenames)
    val_names = set(val_gen.filenames)
    filename_overlap = train_names.intersection(val_names)
    print(f"[*] Filename overlap between train and val sets: {len(filename_overlap)}")

    train_hashes = defaultdict(list)
    for f in train_gen.filenames:
        h = hashlib.md5(open(os.path.join(data_dir, f), 'rb').read()).hexdigest()
        train_hashes[h].append(f)

    val_hashes = defaultdict(list)
    for f in val_gen.filenames:
        h = hashlib.md5(open(os.path.join(data_dir, f), 'rb').read()).hexdigest()
        val_hashes[h].append(f)

    exact_hash_leakage = set(train_hashes.keys()).intersection(set(val_hashes.keys()))
    val_images_with_train_leakage = sum(len(val_hashes[h]) for h in exact_hash_leakage)
    print(f"[*] Exact hash leakage between train and val: {len(exact_hash_leakage)} unique hashes")
    print(f"[*] Validation images affected by train duplicates: {val_images_with_train_leakage} out of {val_gen.n} ({val_images_with_train_leakage / val_gen.n * 100:.2f}%)")

    # 4. Filtered evaluation on clean strictly non-leaked validation images
    clean_val_indices = [
        idx for idx, f in enumerate(val_gen.filenames)
        if hashlib.md5(open(os.path.join(data_dir, f), 'rb').read()).hexdigest() not in train_hashes
    ]
    print(f"[*] Strictly independent (non-leaked) validation images: {len(clean_val_indices)} out of {val_gen.n}")

if __name__ == '__main__':
    audit_dataset()

