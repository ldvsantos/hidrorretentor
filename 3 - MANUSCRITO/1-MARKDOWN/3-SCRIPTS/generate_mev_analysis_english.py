"""
Comparative Morphometric Analysis of SEM Images
Taboa (Typha domingensis) vs Ouricuri (Syagrus coronata)

Script adapted for the systematic review article on geotextiles
Based on the original SEM analysis pipeline from the Bio SAP article
English Version

Author: Diego Vidal
Date: December 2025
"""

import cv2
import numpy as np
from skimage import filters, morphology, measure, feature
from skimage.morphology import skeletonize
from scipy import ndimage
import matplotlib.pyplot as plt
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ComparativeFiberAnalyzer:
    """
    Comparative analysis of Taboa and Ouricuri fibers
    """
    
    def __init__(self, output_dir="./5-DADOS/MEV-ANALISE/resultados_en"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_image(self, image_path):
        """Load SEM image"""
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Could not load: {image_path}")
        
        # Normalize to 0-1
        img_norm = img.astype(float) / 255.0
        return img, img_norm
    
    def analyze_surface_porosity(self, image_norm, sigma=2.0, threshold_factor=0.7):
        """
        Surface porosity analysis
        """
        # Gaussian smoothing
        smoothed = filters.gaussian(image_norm, sigma=sigma)
        
        # Otsu thresholding
        threshold = filters.threshold_otsu(smoothed)
        binary = smoothed < (threshold * threshold_factor)
        
        # Morphological cleaning
        binary_clean = morphology.remove_small_objects(binary, min_size=20)
        binary_clean = morphology.remove_small_holes(binary_clean, area_threshold=10)
        
        # Label regions
        labeled = measure.label(binary_clean)
        regions = measure.regionprops(labeled)
        
        # Calculate metrics
        total_area = image_norm.size
        pore_area = np.sum(binary_clean)
        porosity = (pore_area / total_area) * 100
        
        # Pore metrics
        if regions:
            areas = [r.area for r in regions]
            circularities = [4 * np.pi * r.area / (r.perimeter ** 2) if r.perimeter > 0 else 0 
                           for r in regions]
            
            results = {
                'porosity_percent': round(porosity, 2),
                'num_pores': len(regions),
                'mean_pore_area': round(np.mean(areas), 2),
                'std_pore_area': round(np.std(areas), 2),
                'mean_circularity': round(np.mean(circularities), 3),
                'std_circularity': round(np.std(circularities), 3)
            }
        else:
            results = {
                'porosity_percent': round(porosity, 2),
                'num_pores': 0,
                'mean_pore_area': 0,
                'std_pore_area': 0,
                'mean_circularity': 0,
                'std_circularity': 0
            }
        
        return results, binary_clean, labeled, regions
    
    def analyze_fiber_orientation(self, image_norm, sigma=1.0):
        """
        Fiber orientation analysis
        """
        # Sobel gradients
        sobel_h = filters.sobel_h(filters.gaussian(image_norm, sigma=sigma))
        sobel_v = filters.sobel_v(filters.gaussian(image_norm, sigma=sigma))
        
        # Magnitude and orientation
        magnitude = np.sqrt(sobel_h**2 + sobel_v**2)
        orientation = np.arctan2(sobel_v, sobel_h)
        
        # Filter by magnitude
        threshold = np.percentile(magnitude, 75)
        mask = magnitude > threshold
        
        if np.sum(mask) > 0:
            angles_deg = np.degrees(orientation[mask])
            angles_deg = (angles_deg + 180) % 180  # Normalize 0-180
            
            # Orientation index
            std_angle = np.std(angles_deg)
            orientation_index = 1 - (std_angle / 90.0)
            
            results = {
                'orientation_index': round(orientation_index, 3),
                'mean_angle_deg': round(np.mean(angles_deg), 2),
                'std_angle_deg': round(std_angle, 2)
            }
        else:
            results = {
                'orientation_index': 0,
                'mean_angle_deg': 0,
                'std_angle_deg': 0
            }
        
        return results, magnitude, orientation
    
    def analyze_fiber_structure(self, image_norm, sigma=2.0):
        """
        Fiber structure analysis (skeletonization)
        """
        # Create binary mask
        smoothed = filters.gaussian(image_norm, sigma=sigma)
        threshold = filters.threshold_otsu(smoothed)
        binary = smoothed > threshold
        
        # Skeletonization
        skeleton = skeletonize(binary)
        
        # Fibril density
        fibril_density = np.sum(skeleton) / skeleton.size
        
        # Skeletal length
        skeletal_length = np.sum(skeleton)
        
        # Junction detection (Harris corners)
        skeleton_float = skeleton.astype(float)
        corners = feature.corner_harris(skeleton_float, sigma=2.0)
        corner_threshold = np.percentile(corners, 99.9)
        junctions = corners > corner_threshold
        num_junctions = np.sum(junctions)
        
        results = {
            'fibril_density': round(fibril_density, 5),
            'skeletal_length_px': int(skeletal_length),
            'num_junctions': int(num_junctions)
        }
        
        return results, skeleton, junctions
    
    def analyze_surface_texture(self, image_norm, window_size=15):
        """
        Surface texture analysis (roughness)
        """
        # Roughness by local standard deviation
        kernel = np.ones((window_size, window_size))
        local_mean = ndimage.convolve(image_norm, kernel / kernel.sum(), mode='reflect')
        local_var = ndimage.convolve(image_norm**2, kernel / kernel.sum(), mode='reflect') - local_mean**2
        local_std = np.sqrt(np.maximum(local_var, 0))
        
        roughness_std = np.mean(local_std)
        
        # Roughness by gradient
        gradient_mag = np.sqrt(
            ndimage.sobel(image_norm, axis=0)**2 + 
            ndimage.sobel(image_norm, axis=1)**2
        )
        roughness_grad = np.mean(gradient_mag)
        
        results = {
            'roughness_std': round(roughness_std, 5),
            'roughness_gradient': round(roughness_grad, 5)
        }
        
        return results, local_std
    
    def analyze_single_image(self, image_path, fiber_type="Unknown"):
        """
        Complete analysis of a single image
        """
        print(f"\nAnalyzing {fiber_type}: {Path(image_path).name}")
        
        # Load image
        img, img_norm = self.load_image(image_path)
        
        # Execute analyses
        surface_results, binary, labeled, regions = self.analyze_surface_porosity(img_norm)
        orientation_results, magnitude, angles = self.analyze_fiber_orientation(img_norm)
        structure_results, skeleton, junctions = self.analyze_fiber_structure(img_norm)
        texture_results, roughness_map = self.analyze_surface_texture(img_norm)
        
        # Consolidate results
        results = {
            'fiber_type': fiber_type,
            'image_file': str(Path(image_path).name),
            'timestamp': datetime.now().isoformat(),
            'surface_porosity': surface_results,
            'fiber_orientation': orientation_results,
            'fiber_structure': structure_results,
            'surface_texture': texture_results
        }
        
        # Visualize
        self.visualize_analysis(
            img, img_norm, binary, skeleton, roughness_map, magnitude,
            results, fiber_type
        )
        
        return results
    
    def visualize_analysis(self, img, img_norm, binary, skeleton, 
                          roughness, magnitude, results, fiber_type):
        """
        Create figure with analysis results
        """
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle(f'SEM Morphometric Analysis - {fiber_type}', 
                    fontsize=16, fontweight='bold')
        
        # Original
        axes[0,0].imshow(img, cmap='gray')
        axes[0,0].set_title('Original Image')
        axes[0,0].axis('off')
        
        # Porosity
        axes[0,1].imshow(binary, cmap='gray')
        axes[0,1].set_title(f'Porosity: {results["surface_porosity"]["porosity_percent"]:.2f}%')
        axes[0,1].axis('off')
        
        # Orientation
        axes[0,2].imshow(magnitude, cmap='jet')
        axes[0,2].set_title(f'Orientation (OI={results["fiber_orientation"]["orientation_index"]:.3f})')
        axes[0,2].axis('off')
        
        # Skeleton
        axes[1,0].imshow(skeleton, cmap='gray')
        axes[1,0].set_title(f'Fibrillar Structure (D={results["fiber_structure"]["fibril_density"]:.4f})')
        axes[1,0].axis('off')
        
        # Roughness
        axes[1,1].imshow(roughness, cmap='hot')
        axes[1,1].set_title(f'Roughness (σ={results["surface_texture"]["roughness_std"]:.4f})')
        axes[1,1].axis('off')
        
        # Summary text
        axes[1,2].axis('off')
        summary_text = f"""
        SUMMARY - {fiber_type}
        
        Porosity:
          • Total: {results["surface_porosity"]["porosity_percent"]:.2f}%
          • No. pores: {results["surface_porosity"]["num_pores"]}
          • Mean area: {results["surface_porosity"]["mean_pore_area"]:.1f} px²
          
        Orientation:
          • Index: {results["fiber_orientation"]["orientation_index"]:.3f}
          • Angle: {results["fiber_orientation"]["mean_angle_deg"]:.1f}°
          
        Structure:
          • Density: {results["fiber_structure"]["fibril_density"]:.4f}
          • Junctions: {results["fiber_structure"]["num_junctions"]}
          
        Texture:
          • Roughness: {results["surface_texture"]["roughness_std"]:.4f}
        """
        axes[1,2].text(0.1, 0.5, summary_text, fontsize=10, 
                      verticalalignment='center', family='monospace')
        
        plt.tight_layout()
        
        # Save
        filename = f"analysis_{fiber_type}_{Path(results['image_file']).stem}_en.png"
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Figure saved: {filename}")
    
    def compare_fibers(self, taboa_results, ouricuri_results):
        """
        Quantitative comparison between Taboa and Ouricuri
        """
        comparison = {
            'comparison_date': datetime.now().isoformat(),
            'taboa': taboa_results,
            'ouricuri': ouricuri_results,
            'differences': {}
        }
        
        # Calculate percentage differences
        metrics = [
            ('surface_porosity', 'porosity_percent'),
            ('surface_porosity', 'num_pores'),
            ('fiber_orientation', 'orientation_index'),
            ('fiber_structure', 'fibril_density'),
            ('surface_texture', 'roughness_std')
        ]
        
        for category, metric in metrics:
            val_taboa = taboa_results[category][metric]
            val_ouricuri = ouricuri_results[category][metric]
            
            if val_taboa != 0:
                diff_percent = ((val_ouricuri - val_taboa) / val_taboa) * 100
            else:
                diff_percent = 0 if val_ouricuri == 0 else 100
            
            comparison['differences'][f'{category}_{metric}'] = {
                'taboa': val_taboa,
                'ouricuri': val_ouricuri,
                'diff_percent': round(diff_percent, 2)
            }
        
        # Save comparison
        comp_file = self.output_dir / f"comparison_taboa_ouricuri_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(comp_file, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        
        print(f"\nComparison saved: {comp_file.name}")
        
        # Visualize comparison
        self.plot_comparison(comparison)
        
        return comparison
    
    def plot_comparison(self, comparison):
        """
        Comparative plot between fibers
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Morphometric Comparison: Taboa vs Ouricuri', 
                    fontsize=14, fontweight='bold')
        
        # Porosity
        ax = axes[0,0]
        por_t = comparison['taboa']['surface_porosity']['porosity_percent']
        por_o = comparison['ouricuri']['surface_porosity']['porosity_percent']
        ax.bar(['Taboa', 'Ouricuri'], [por_t, por_o], color=['#2E7D32', '#D84315'])
        ax.set_ylabel('Porosity (%)')
        ax.set_title('Surface Porosity')
        ax.grid(axis='y', alpha=0.3)
        
        # Orientation
        ax = axes[0,1]
        ori_t = comparison['taboa']['fiber_orientation']['orientation_index']
        ori_o = comparison['ouricuri']['fiber_orientation']['orientation_index']
        ax.bar(['Taboa', 'Ouricuri'], [ori_t, ori_o], color=['#2E7D32', '#D84315'])
        ax.set_ylabel('Orientation Index')
        ax.set_title('Fibrillar Orientation')
        ax.set_ylim([0, 1])
        ax.grid(axis='y', alpha=0.3)
        
        # Fibril density
        ax = axes[1,0]
        den_t = comparison['taboa']['fiber_structure']['fibril_density']
        den_o = comparison['ouricuri']['fiber_structure']['fibril_density']
        ax.bar(['Taboa', 'Ouricuri'], [den_t, den_o], color=['#2E7D32', '#D84315'])
        ax.set_ylabel('Fibrillar Density')
        ax.set_title('Fibrillar Structure')
        ax.grid(axis='y', alpha=0.3)
        
        # Roughness
        ax = axes[1,1]
        rug_t = comparison['taboa']['surface_texture']['roughness_std']
        rug_o = comparison['ouricuri']['surface_texture']['roughness_std']
        ax.bar(['Taboa', 'Ouricuri'], [rug_t, rug_o], color=['#2E7D32', '#D84315'])
        ax.set_ylabel('Roughness (σ)')
        ax.set_title('Surface Texture')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Save
        filename = f"comparative_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_en.png"
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Comparative plot saved: {filename}")


def main():
    """
    Main execution
    """
    print("="*70)
    print(" Comparative SEM Morphometric Analysis")
    print(" Taboa (Typha domingensis) vs Ouricuri (Syagrus coronata)")
    print("="*70)
    
    # Paths
    base_dir = Path("./5-DADOS/MEV-ANALISE")
    taboa_dir = base_dir / "imagens-taboa"
    ouricuri_dir = base_dir / "imagens-ouricuri"
    
    # Check directories
    if not taboa_dir.exists() or not list(taboa_dir.glob("*.tif")):
        print(f"\nWARNING: No images found in {taboa_dir}")
        print("Copy Taboa SEM TIF images to this directory")
    
    if not ouricuri_dir.exists() or not list(ouricuri_dir.glob("*.tif")):
        print(f"\nWARNING: No images found in {ouricuri_dir}")
        print("Copy Ouricuri SEM TIF images to this directory")
    
    # Create analyzer
    analyzer = ComparativeFiberAnalyzer()
    
    # Analyze first image of each fiber (if available)
    taboa_images = list(taboa_dir.glob("*.tif"))
    ouricuri_images = list(ouricuri_dir.glob("*.tif"))
    
    results_taboa = None
    results_ouricuri = None
    
    if taboa_images:
        print(f"\nFound {len(taboa_images)} Taboa images")
        results_taboa = analyzer.analyze_single_image(taboa_images[0], "Typha domingensis")
    
    if ouricuri_images:
        print(f"\nFound {len(ouricuri_images)} Ouricuri images")
        results_ouricuri = analyzer.analyze_single_image(ouricuri_images[0], "Syagrus coronata")
    
    # Comparison
    if results_taboa and results_ouricuri:
        print("\n" + "="*70)
        print(" FIBER COMPARISON")
        print("="*70)
        comparison = analyzer.compare_fibers(results_taboa, results_ouricuri)
        
        print("\nMain differences:")
        for key, value in comparison['differences'].items():
            print(f"  {key}: {value['diff_percent']:+.1f}%")
    
    print("\n" + "="*70)
    print(" Analysis completed!")
    print(f" Results saved in: {analyzer.output_dir}")
    print("="*70)


if __name__ == "__main__":
    main()
