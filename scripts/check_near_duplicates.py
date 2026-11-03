import os
import cv2
import numpy as np
import tensorflow as tf

def compute_dhash_64(img_path, hash_size=8):
    """Compute 64-bit difference hash (dhash) as a uint64 integer."""
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    resized = cv2.resize(img, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)
    diff = resized[:, 1:] > resized[:, :-1]
    # Pack 64 boolean values into uint64
    packed = 0
    for bit in diff.flatten():
        packed = (packed << 1) | int(bit)
    return packed

def main():
    data_dir = os.path.expanduser(
        '~/.cache/kagglehub/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images/versions/1/lung_colon_image_set/colon_image_sets'
    )
    print(f"[*] Computing perceptual dhashes for LC25000 images in: {data_dir}")

    datagen = tf.keras.preprocessing.image.ImageDataGenerator(validation_split=0.2)
    train_gen = datagen.flow_from_directory(
        data_dir, subset='training', classes=['colon_aca', 'colon_n'], shuffle=False
    )
    val_gen = datagen.flow_from_directory(
        data_dir, subset='validation', classes=['colon_aca', 'colon_n'], shuffle=False
    )

    print("[*] Hashing 8,000 training images...")
    train_hashes = []
    for f in train_gen.filenames:
        h = compute_dhash_64(os.path.join(data_dir, f))
        train_hashes.append(h)
    train_hashes = np.array(train_hashes, dtype=np.uint64)

    print("[*] Hashing 2,000 validation images...")
    val_hashes = []
    for f in val_gen.filenames:
        h = compute_dhash_64(os.path.join(data_dir, f))
        val_hashes.append(h)
    val_hashes = np.array(val_hashes, dtype=np.uint64)

    # Fast bitwise Hamming distance computation: bit_count(val ^ train)
    print("[*] Computing pairwise Hamming distance matrix (2,000 x 8,000 = 16,000,000 pairs)...")
    
    exact_perceptual_matches = 0   # Hamming distance == 0
    near_dups_dist_le_2 = 0        # Hamming distance <= 2
    near_dups_dist_le_4 = 0        # Hamming distance <= 4

    min_distances = []

    # Process in chunks of 200 validation images to conserve memory
    chunk_size = 200
    for i in range(0, len(val_hashes), chunk_size):
        chunk = val_hashes[i:i + chunk_size]
        # XOR broadcast: (chunk_size, 8000)
        xor_matrix = np.bitwise_xor(chunk[:, np.newaxis], train_hashes[np.newaxis, :])
        
        # Vectorized bit count (popcount) on 64-bit integers
        # In NumPy, bit count can be computed via unpackbits on uint8 view
        uint8_view = xor_matrix.view(np.uint8)
        # popcount table for 0..255
        popcnt_table = np.array([bin(x).count('1') for x in range(256)], dtype=np.uint8)
        hamming_matrix = popcnt_table[uint8_view].reshape(chunk.shape[0], len(train_hashes), 8).sum(axis=-1)
        
        min_dist_per_val = hamming_matrix.min(axis=1)
        min_distances.extend(min_dist_per_val)

        exact_perceptual_matches += np.sum(min_dist_per_val == 0)
        near_dups_dist_le_2 += np.sum(min_dist_per_val <= 2)
        near_dups_dist_le_4 += np.sum(min_dist_per_val <= 4)

    print("\n" + "="*60)
    print("PERCEPTUAL HASH (dHash) AUDIT RESULTS")
    print("="*60)
    print(f"Total Validation Images Audited: {len(val_hashes)}")
    print(f"Exact Perceptual Matches (Hamming dist == 0): {exact_perceptual_matches} ({exact_perceptual_matches / len(val_hashes) * 100:.2f}%)")
    print(f"Near-Duplicates (Hamming dist <= 2 bits):      {near_dups_dist_le_2} ({near_dups_dist_le_2 / len(val_hashes) * 100:.2f}%)")
    print(f"Near-Duplicates (Hamming dist <= 4 bits):      {near_dups_dist_le_4} ({near_dups_dist_le_4 / len(val_hashes) * 100:.2f}%)")
    print(f"Median Minimum Hamming Distance to Train Set: {np.median(min_distances):.1f} bits")
    print(f"Mean Minimum Hamming Distance to Train Set:   {np.mean(min_distances):.2f} bits")
    print("="*60)

if __name__ == '__main__':
    main()

