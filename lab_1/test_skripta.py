import os
import subprocess

# Paths
test_folder = r"D:\Fran\Documents\FER\5. semestar\PPJ\lab_vjezbe\1_lab_vjezba\primjeri"
program_path = r"D:\Fran\Documents\FER\5. semestar\PPJ\lab_vjezbe\1_lab_vjezba\1_lab_vjezba_ppj\LeksickiAnalizator.py"
results_file = os.path.join(test_folder, "RESULTS.txt")


# Function to run a single test
def run_test(test_in, test_out):
    # Pokreni LeksickiAnalizator.py s ulaznom datotekom i hvataj izlaz
    process = subprocess.Popen(
        ['python', program_path],
        stdin=open(test_in, 'r'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    # Pročitaj očekivani izlaz iz test.out
    with open(test_out, 'r') as f:
        expected_output = f.read()

    # Uklanjanje suvišnih praznih linija i razmaka
    clean_stdout = stdout.decode().strip().splitlines()
    clean_expected = expected_output.strip().splitlines()

    # Usporedba ignorirajući prazne linije i razmake
    clean_stdout = [line.strip() for line in clean_stdout if line.strip()]
    clean_expected = [line.strip() for line in clean_expected if line.strip()]

    return clean_stdout == clean_expected, clean_stdout, clean_expected, stderr


# Prepare the results file
with open(results_file, 'w') as results:
    results.write("Test Results:\n")

    # Loop through all test folders
    for folder in os.listdir(test_folder):
        folder_path = os.path.join(test_folder, folder)
        if os.path.isdir(folder_path):
            test_in = os.path.join(folder_path, 'test.in')
            test_out = os.path.join(folder_path, 'test.out')

            # Check if both test.in and test.out exist
            if os.path.exists(test_in) and os.path.exists(test_out):
                # Run the test
                passed, output, expected_output, errors = run_test(test_in, test_out)

                # Write the result to the file
                results.write(f"Test {folder}: {'PASSED' if passed else 'FAILED'}\n")
                if not passed:
                    results.write(f"Expected:\n{expected_output}\n")
                    results.write(f"Got:\n{output}\n")
                    if errors:
                        results.write(f"Errors:\n{errors.decode()}\n")
                results.write("\n")

print(f"All test results have been written to {results_file}")
