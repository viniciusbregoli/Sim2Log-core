"""
Simple test file for Sim2Log Core.

Generates synthetic event logs from a real XES file.

Usage:
    python test.py <xes_file>
    python test.py bases/running-example.xes
"""

import argparse
import subprocess
import sys
from pathlib import Path
from process_mining import ProcessMiner
from simulation import LogSimulator
from validation import LogValidator
from models import SimulationConfig


def show_image(image_path):
    try:
        subprocess.run(["xdg-open", str(image_path)], check=False)
        print(f"  Opening image viewer for {image_path}")
    except Exception as e:
        print(f"  Could not auto-open image: {e}")


def test_basic_workflow(input_file, num_cases=50):
    """Test the basic mine -> simulate -> validate workflow.
    
    Args:
        input_file: Path to XES file to process
        num_cases: Number of synthetic cases to generate
    """
    input_file = Path(input_file)
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        if Path("bases").exists():
            print("\nAvailable files in bases/:")
            for f in Path("bases").glob("*.xes"):
                print(f"  - {f}")
        sys.exit(1)
    
    print("="*60)
    print("MINERAÇÃO DE PROCESSOS")
    print("="*60)
    
    # Step 1: Mine process
    print("\n[1/3] Mining process model...")
    model_image_path = Path("output/process-model.png")
    miner = ProcessMiner(verbose=True)
    model = miner.mine_process(
        input_file, 
        variant_filter=0.8,
        save_model_image=model_image_path
    )
    
    # Show the process model
    print("\nDisplaying process model...")
    show_image(model_image_path)
    
    # Step 2: Simulate
    print("="*60)
    print("SIMULAÇÃO DE PROCESSOS")
    print("="*60)
    
    print(f"\n[2/3] Simulating synthetic log ({num_cases} cases)...")
    config = SimulationConfig(num_cases=num_cases, random_seed=42)
    simulator = LogSimulator(config, verbose=True)
    result = simulator.simulate(
        model, 
        output_dir="output", 
        output_prefix="test-synthetic"
    )
    
    # Step 3: Validate
    print("="*60)
    print("VALIDAÇÃO DE PROCESSOS")
    print("="*60)
    
    print("\n[3/3] Validating quality...")
    validator = LogValidator(verbose=True)
    validation = validator.validate(input_file, result.xes_path)
    
    # Results
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"✓ Cases: {result.num_cases_generated}")
    print(f"✓ Events: {result.num_events_generated}")
    print(f"✓ Similarity: {validation.similarity_percentage:.1f}%")
    print(f"✓ Fitness: {validation.fitness:.3f}")
    
    if validation.fitness >= 0.7:
        print("\n✓ TEST PASSED - Good quality synthetic log generated!")
    else:
        print("\n⚠ TEST WARNING - Low similarity, check parameters")
    
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate synthetic event logs from a real XES file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test.py bases/running-example.xes
  python test.py bases/patient_treatment.xes
  python test.py path/to/your/log.xes
        """
    )
    parser.add_argument(
        "xes_file",
        type=str,
        help="Path to the input XES file"
    )
    parser.add_argument(
        "-n", "--num-cases",
        type=int,
        default=50,
        help="Number of synthetic cases to generate (default: 50)"
    )
    
    args = parser.parse_args()
    test_basic_workflow(args.xes_file, args.num_cases)

