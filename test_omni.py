"""
Quick test to verify OMNI is working with all phases.
"""

print("🤖 Testing Project OMNI - All Phases")
print("=" * 50)

# Test imports
try:
    from src.core.brain import OmniBrain
    print("✅ Phase 1: OmniBrain imported")
    
    from src.tools.data_analysis import DataAnalysisTools
    print("✅ Phase 2: Data Analysis tools imported")
    
    from src.tools.web_scraping import WebScrapingTools
    print("✅ Phase 2: Web Scraping tools imported")
    
    from src.executors.computer_use import ComputerUseModule
    print("✅ Phase 3: Computer Use module imported")
    
    from src.perception.voice import VoiceModule
    print("✅ Phase 4: Voice module imported")
    
    from src.tools.browser import BrowserAutomation
    print("✅ Phase 5: Browser automation imported")
    
    from src.tools.api_integrations import APIIntegrations
    print("✅ Phase 5: API integrations imported")
    
    print("\n" + "=" * 50)
    print("🎉 ALL MODULES LOADED SUCCESSFULLY!")
    print("=" * 50)
    
    # Initialize OmniBrain
    print("\n🧠 Initializing OmniBrain...")
    brain = OmniBrain()
    print("✅ OmniBrain initialized with all phases!")
    
    print("\n📊 Available capabilities:")
    print("  • Open Interpreter (code execution)")
    print("  • Data Analysis (pandas, matplotlib)")
    print("  • Web Scraping (BeautifulSoup)")
    print("  • GUI Automation (PyAutoGUI)")
    print("  • Voice Output (pyttsx3)")
    print("  • Browser Automation (Playwright)")
    print("  • API Integrations (placeholders)")
    
    print("\n✨ Project OMNI is ready to use!")
    print("Run: py -3.9 src\\cli.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
