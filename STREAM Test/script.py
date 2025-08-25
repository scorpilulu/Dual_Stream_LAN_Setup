# Create a diagnostic comparison table for the user's situation
import csv

comparison_data = [
    ["Factor", "Working Boot", "Non-Working Boot", "Impact", "Solution"],
    ["Graphics Drivers", "Newer/Proper drivers", "Older/Generic drivers", "Critical", "Update graphics drivers"],
    ["Windows Version", "Windows 10/11 latest", "Older Windows build", "High", "Run Windows Update"],
    ["DirectX Runtime", "Latest DirectX 12", "Older DirectX runtime", "Critical", "Install DirectX Runtime"],
    ["Windows Updates", "Fully updated", "Missing updates", "High", "Install all updates"],
    ["WDDM Version", "WDDM 2.0+", "WDDM 1.x", "Critical", "Update display drivers"],
    ["System Configuration", "Clean install", "Upgraded/modified", "Medium", "Check display settings"],
    ["Registry Differences", "Clean registry", "Modified registry", "Low", "Registry cleanup"],
    ["Third-party Software", "Minimal software", "Conflicting software", "Medium", "Check for conflicts"]
]

with open('boot_comparison_analysis.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(comparison_data)

print("✅ Created boot comparison analysis")
print("\nMost Likely Causes (in order of probability):")
print("1. Graphics driver version differences")
print("2. Windows build/update level differences") 
print("3. DirectX runtime version differences")
print("4. Windows Display Driver Model (WDDM) version differences")