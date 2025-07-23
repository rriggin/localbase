"""
Google Maps List Scraper - Simplified Address Extractor

This module contains a simple scraper for extracting addresses from Google Maps public lists.
"""

import time
import csv
import logging
from typing import List, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import json

# Configure global logger for standalone functions
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class AddressItem:
    """Data class for storing address information."""
    address: str
    name: Optional[str] = None


class GoogleMapsListScraper:
    """
    A simple scraper for extracting addresses from Google Maps public lists.
    """
    
    def __init__(self, headless: bool = True, timeout: int = 10):
        """
        Initialize the Google Maps list scraper.
        
        Args:
            headless: Whether to run browser in headless mode
            timeout: Timeout for web element waits in seconds
        """
        self.timeout = timeout
        self.driver = None
        self.headless = headless
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the scraper."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Set up the Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
            
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Remove profile-specific arguments for now - will use clean session
        # Note: Make sure your Google Maps list is set to "Anyone with the link can view"
        
        # Set Chrome binary path for macOS
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        return webdriver.Chrome(options=chrome_options)
    
    def start(self):
        """Start the browser session."""
        self.logger.info("Starting Google Maps list scraper...")
        self.driver = self._setup_driver()
        self.logger.info("Browser session started successfully")
    
    def stop(self):
        """Stop the browser session."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("Browser session stopped")
    
    def scrape_addresses(self, url: str) -> List[AddressItem]:
        """
        Scrape addresses from a Google Maps list URL.
        Uses multiple page reloads to capture all addresses in large lists.
        
        Args:
            url: The Google Maps list URL to scrape
            
        Returns:
            List of AddressItem objects containing address information
        """
        try:
            all_unique_addresses = {}  # Use dict to track unique addresses across reloads
            
            # Try multiple page loads to capture different address subsets
            max_reloads = 5  # Try up to 5 reloads
            
            for reload_attempt in range(max_reloads):
                self.logger.info(f"\n=== PAGE LOAD {reload_attempt + 1}/{max_reloads} ===")
                
                # Load the page
                self.driver.get(url)
                
                # Wait for the page to load completely
                time.sleep(8)  # Longer wait for better loading
                
                # Scroll to load more content
                self._perform_comprehensive_scrolling()
                
                # For the first load, try enhanced scrolling method for large lists
                if reload_attempt == 0:
                    # Try the enhanced scrolling method first
                    enhanced_addresses = self._scrape_with_scrolling()
                    if len(enhanced_addresses) > 100:
                        self.logger.info(f"Enhanced scrolling found {len(enhanced_addresses)} addresses - using this method")
                        return enhanced_addresses
                
                # Extract addresses from this page load using enhanced method
                raw_addresses = enhanced_address_extraction(self.driver)
                
                # Convert raw addresses to AddressItem objects
                addresses_this_load = []
                for addr_text in raw_addresses:
                    addr_item = self._create_address_item(addr_text)
                    addresses_this_load.append(addr_item)
                
                # Add new unique addresses
                new_addresses_count = 0
                for addr_item in addresses_this_load:
                    if addr_item.address not in all_unique_addresses:
                        all_unique_addresses[addr_item.address] = addr_item
                        new_addresses_count += 1
                
                total_unique = len(all_unique_addresses)
                self.logger.info(f"Load {reload_attempt + 1}: Found {len(addresses_this_load)} addresses, {new_addresses_count} new unique (Total unique: {total_unique})")
                
                # If we haven't found new addresses in the last 2 reloads, stop
                if reload_attempt >= 2 and new_addresses_count == 0:
                    self.logger.info("No new addresses found in recent reloads, stopping early")
                    break
                
                # Brief pause between reloads
                if reload_attempt < max_reloads - 1:
                    time.sleep(3)
            
            # Convert back to list
            final_addresses = list(all_unique_addresses.values())
            
            self.logger.info(f"\n=== FINAL RESULTS ===")
            self.logger.info(f"Total unique addresses found across all reloads: {len(final_addresses)}")
            
            return final_addresses
            
        except Exception as e:
            self.logger.error(f"Error scraping addresses: {str(e)}")
            raise
    
    def get_list_title(self, url: str) -> str:
        """
        Extract the title/name of the Google Maps list.
        
        Args:
            url: The Google Maps list URL
            
        Returns:
            The list title, or "Google Maps List" if not found
        """
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Try multiple selectors for the list title
            title_selectors = [
                "h1[data-attrid='title']",
                "h1",
                "[data-attrid='title']",
                ".fontHeadlineLarge",
                ".fontHeadlineMedium",
                "title"
            ]
            
            for selector in title_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    title = element.text.strip()
                    if title and len(title) > 0:
                        self.logger.info(f"Found list title: {title}")
                        return title
                except NoSuchElementException:
                    continue
            
            # Fallback: try to get from page title
            try:
                page_title = self.driver.title
                if page_title and "Google Maps" not in page_title:
                    return page_title
            except:
                pass
                
            return "Google Maps List"
            
        except Exception as e:
            self.logger.warning(f"Could not extract list title: {e}")
            return "Google Maps List"
    
    def _perform_comprehensive_scrolling(self):
        """Perform comprehensive scrolling to load more content."""
        self.logger.info("Performing comprehensive scrolling...")
        
        # Multiple scrolling strategies
        strategies = [
            # Strategy 1: Slow scroll down
            lambda: self._scroll_strategy_slow_down(),
            # Strategy 2: Fast scroll to bottom then back up
            lambda: self._scroll_strategy_fast_sweep(),
            # Strategy 3: Multiple small scrolls with pauses
            lambda: self._scroll_strategy_incremental(),
        ]
        
        for i, strategy in enumerate(strategies, 1):
            self.logger.info(f"Scrolling strategy {i}/3...")
            try:
                strategy()
                time.sleep(2)  # Pause between strategies
            except Exception as e:
                self.logger.warning(f"Scrolling strategy {i} failed: {e}")
    
    def _scroll_strategy_slow_down(self):
        """Scroll slowly down the page."""
        for i in range(10):
            self.driver.execute_script(f"window.scrollTo(0, {i * 500});")
            time.sleep(1)
    
    def _scroll_strategy_fast_sweep(self):
        """Fast scroll to bottom then back to top."""
        # Scroll to bottom
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        # Scroll back to top
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    
    def _scroll_strategy_incremental(self):
        """Small incremental scrolls with pauses."""
        current_height = 0
        scroll_increment = 200
        
        for i in range(20):
            current_height += scroll_increment
            self.driver.execute_script(f"window.scrollTo(0, {current_height});")
            time.sleep(0.5)
    
    def _extract_addresses_from_page_source(self, page_source: str) -> List[AddressItem]:
        """Extract addresses from page source using comprehensive methods."""
        addresses = []
        
        # Method 1: Extract from JavaScript arrays and objects
        import re
        import json
        
        # Pattern 1: Find JSON arrays containing address data
        # Look for patterns like ["address", lat, lng, "name", ...]
        json_array_pattern = r'\[([^[\]]*(?:\[[^\]]*\][^[\]]*)*)\]'
        json_matches = re.findall(json_array_pattern, page_source)
        
        for match in json_matches:
            try:
                # Look for address patterns within each array
                if 'Lee\'s Summit' in match or 'MO 64081' in match:
                    # Extract address patterns from this JSON structure
                    address_in_json = re.search(r'"([^"]*\d{3,5}[^"]*Lee\'s Summit[^"]*64081[^"]*)"', match)
                    if address_in_json:
                        full_address = address_in_json.group(1)
                        # Clean up the address
                        full_address = full_address.replace('\\', '').strip()
                        if full_address not in [addr.address for addr in addresses]:
                            addresses.append(self._create_address_item(full_address))
            except Exception as e:
                continue
        
        # Method 2: Extract from quoted strings with address patterns
        # Pattern for full addresses in quotes
        quoted_address_pattern = r'"([^"]*\d{3,5}[^"]*Lee\'s Summit[^"]*MO[^"]*64081[^"]*)"'
        quoted_matches = re.findall(quoted_address_pattern, page_source)
        
        for match in quoted_matches:
            clean_address = match.replace('\\', '').strip()
            # Ensure it looks like a real address
            if re.match(r'^\d{3,5}\s+\w+', clean_address):
                if clean_address not in [addr.address for addr in addresses]:
                    addresses.append(self._create_address_item(clean_address))
        
        self.logger.info("2. Quoted strings - extracted from quoted address strings")
        
        # Method 3: Extract from JavaScript variable assignments
        # Look for patterns like var addresses = ["...", "...", ...]
        js_var_pattern = r'(?:var|let|const)\s+\w*[Aa]ddress\w*\s*=\s*\[([^\]]+)\]'
        js_var_matches = re.findall(js_var_pattern, page_source)
        
        for match in js_var_matches:
            # Extract quoted strings from the array
            address_strings = re.findall(r'"([^"]*Lee\'s Summit[^"]*64081[^"]*)"', match)
            for addr_str in address_strings:
                clean_address = addr_str.replace('\\', '').strip()
                if re.match(r'^\d{3,5}\s+\w+', clean_address):
                    if clean_address not in [addr.address for addr in addresses]:
                        addresses.append(self._create_address_item(clean_address))
        
        self.logger.info("3. JS variables - extracted from JavaScript variable assignments")
        
        # Method 4: Extract from data attributes
        # Look for data-address or similar attributes
        data_attr_pattern = r'data-[^=]*address[^=]*="([^"]*Lee\'s Summit[^"]*64081[^"]*)"'
        data_attr_matches = re.findall(data_attr_pattern, page_source, re.IGNORECASE)
        
        for match in data_attr_matches:
            clean_address = match.replace('\\', '').strip()
            if re.match(r'^\d{3,5}\s+\w+', clean_address):
                if clean_address not in [addr.address for addr in addresses]:
                    addresses.append(self._create_address_item(clean_address))
        
        self.logger.info("4. Data attributes - extracted from HTML data attributes")
        
        # Method 5: Broad search for any address-like patterns
        # More comprehensive pattern that catches variations
        broad_pattern = r'(\d{3,5}\s+[A-Za-z0-9\s]+(?:St|Street|Dr|Drive|Rd|Road|Ave|Avenue|Ct|Court|Cir|Circle|Ln|Lane|Pl|Place|Terrace)[^,]*,?\s*Lee\'s Summit[^,]*,?\s*MO[^,]*,?\s*64081)'
        broad_matches = re.findall(broad_pattern, page_source, re.IGNORECASE)
        
        for match in broad_matches:
            clean_address = re.sub(r'\s+', ' ', match).strip()
            # Remove any trailing commas or periods
            clean_address = clean_address.rstrip('.,')
            if clean_address not in [addr.address for addr in addresses]:
                addresses.append(self._create_address_item(clean_address))
        
        self.logger.info("5. Broad search - comprehensive pattern matching")
        
        # Method 6: Extract from window/global objects
        # Look for window.something = {addresses: [...]} patterns
        global_obj_pattern = r'window\.[^=]+=\s*\{[^}]*addresses?[^}]*\}|window\.[^=]+=\s*\[[^\]]*Lee\'s Summit[^\]]*\]'
        global_obj_matches = re.findall(global_obj_pattern, page_source, re.IGNORECASE | re.DOTALL)
        
        for match in global_obj_matches:
            # Extract addresses from the global object
            addr_in_global = re.findall(r'"([^"]*\d{3,5}[^"]*Lee\'s Summit[^"]*64081[^"]*)"', match)
            for addr in addr_in_global:
                clean_address = addr.replace('\\', '').strip()
                if re.match(r'^\d{3,5}\s+\w+', clean_address):
                    if clean_address not in [addr.address for addr in addresses]:
                        addresses.append(self._create_address_item(clean_address))
        
        self.logger.info("6. Global objects - extracted from window global variables")
        
        # Method 7: Fallback patterns - catch any remaining addresses
        fallback_pattern = r'[\'"]([\d\w\s]+,?\s*Lee\'s Summit,?\s*MO,?\s*64081)[\'""]'
        fallback_matches = re.findall(fallback_pattern, page_source, re.IGNORECASE)
        
        for match in fallback_matches:
            clean_address = re.sub(r'\s+', ' ', match).strip()
            # Ensure it starts with a number (house number)
            if re.match(r'^\d{3,5}\s+', clean_address):
                if clean_address not in [addr.address for addr in addresses]:
                    addresses.append(self._create_address_item(clean_address))
        
        self.logger.info("7. Fallback patterns - caught any remaining addresses")
        
        # Remove duplicates and return unique addresses
        unique_addresses = []
        seen_addresses = set()
        
        for addr in addresses:
            if addr.address not in seen_addresses:
                unique_addresses.append(addr)
                seen_addresses.add(addr.address)
        
        return unique_addresses
    
    def _create_address_item(self, full_address: str) -> AddressItem:
        """
        Create an AddressItem from a full address string.
        """
        try:
            # Clean up the address - remove ", USA" suffix if present
            clean_address = full_address.replace(', USA', '').strip()
            
            return AddressItem(
                address=clean_address,
                name=None
            )
        except Exception as e:
            self.logger.warning(f"Error creating address item '{full_address}': {e}")
            return AddressItem(
                address=full_address,
                name=None
            )
    
    def _scrape_with_scrolling(self) -> List[AddressItem]:
        """
        Enhanced scrolling method to handle large Google Maps lists with virtual scrolling.
        Targets specific list containers and uses more aggressive scrolling.
        """
        self.logger.info("Using enhanced scrolling method for large list extraction...")
        all_addresses = set()
        
        # Potential scrollable container selectors for Google Maps lists
        scrollable_selectors = [
            ".kA9KIf",  # Main scrollable content class
            ".DxyBCb",  # List display container
            ".aIFcqe",  # Content area
            ".m6QErb.DxyBCb",  # Combined selectors
            "[role='main']",  # Main content area
            ".PLbyfe .kA9KIf"  # More specific path
        ]
        
        scrollable_element = None
        
        # Find the scrollable container
        for selector in scrollable_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    scrollable_element = elements[0]
                    self.logger.info(f"Found scrollable container with selector: {selector}")
                    break
            except Exception as e:
                continue
        
        if not scrollable_element:
            self.logger.warning("Could not find specific scrollable container, using document body")
            scrollable_element = self.driver.find_element(By.TAG_NAME, "body")
        
        # Enhanced scrolling parameters for large lists
        max_scrolls = 100  # Increased for large lists
        scroll_attempts = 0
        consecutive_no_new_addresses = 0
        max_no_new_consecutive = 10  # Stop if no new addresses found for 10 consecutive scrolls
        
        self.logger.info(f"Starting enhanced scrolling (max {max_scrolls} attempts)")
        
        # Initial extraction
        current_addresses = self._extract_addresses_from_page_source(self.driver.page_source)
        for addr_item in current_addresses:
            all_addresses.add(addr_item.address)
        
        self.logger.info(f"Initial addresses found: {len(all_addresses)}")
        
        while scroll_attempts < max_scrolls and consecutive_no_new_addresses < max_no_new_consecutive:
            prev_count = len(all_addresses)
            
            try:
                # Multiple scrolling strategies
                if scroll_attempts % 3 == 0:
                    # Strategy 1: Scroll within the specific container
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;", 
                        scrollable_element
                    )
                elif scroll_attempts % 3 == 1:
                    # Strategy 2: Use scrollIntoView on the last visible address
                    try:
                        address_elements = self.driver.find_elements(By.CSS_SELECTOR, ".SMP2wb, .H1bDYe, .fontHeadlineSmall")
                        if address_elements:
                            last_element = address_elements[-1]
                            self.driver.execute_script("arguments[0].scrollIntoView(false);", last_element)
                    except:
                        # Fallback to container scrolling
                        self.driver.execute_script("arguments[0].scrollTop += 500;", scrollable_element)
                else:
                    # Strategy 3: Aggressive page down within container
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollTop + (arguments[0].clientHeight * 1.5);", 
                        scrollable_element
                    )
                
                # Wait for content to load
                time.sleep(2)
                
                # Extract newly loaded addresses
                page_source = self.driver.page_source
                current_addresses = self._extract_addresses_from_page_source(page_source)
                
                for addr_item in current_addresses:
                    all_addresses.add(addr_item.address)
                
                new_count = len(all_addresses)
                if new_count > prev_count:
                    self.logger.info(f"Scroll {scroll_attempts + 1}: Found {new_count - prev_count} new addresses (total: {new_count})")
                    consecutive_no_new_addresses = 0
                else:
                    consecutive_no_new_addresses += 1
                    if consecutive_no_new_addresses == 5:
                        self.logger.info(f"No new addresses for 5 scrolls, trying larger scroll amount...")
                        # Try a much larger scroll
                        self.driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollTop + (arguments[0].clientHeight * 3);", 
                            scrollable_element
                        )
                        time.sleep(3)
                
                scroll_attempts += 1
                
                # Progress indicator
                if scroll_attempts % 10 == 0:
                    self.logger.info(f"Progress: {scroll_attempts}/{max_scrolls} scrolls completed, {len(all_addresses)} addresses found")
                
            except Exception as e:
                self.logger.error(f"Error during scroll {scroll_attempts}: {str(e)}")
                scroll_attempts += 1
                time.sleep(1)
        
        if consecutive_no_new_addresses >= max_no_new_consecutive:
            self.logger.info(f"Stopped scrolling: No new addresses found for {max_no_new_consecutive} consecutive attempts")
        else:
            self.logger.info(f"Completed all {max_scrolls} scroll attempts")
        
        self.logger.info(f"Enhanced scrolling completed. Total addresses found: {len(all_addresses)}")
        
        # Convert back to AddressItem format
        final_addresses = []
        for addr in all_addresses:
            final_addresses.append(AddressItem(address=addr))
        
        return final_addresses
    
    def _extract_addresses(self) -> List[AddressItem]:
        """Extract addresses from the current list page."""
        addresses = []
        
        try:
            # Find all list item elements
            list_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "[role='listitem']"
            )
            
            self.logger.info(f"Found {len(list_elements)} list items")
            
            for i, element in enumerate(list_elements):
                try:
                    self.logger.info(f"Processing item {i+1}/{len(list_elements)}")
                    
                    # Extract address from the list item
                    address = self._extract_address_from_element(element)
                    name = self._extract_name_from_element(element)
                    
                    if address:
                        addresses.append(AddressItem(address=address, name=name))
                        self.logger.info(f"Found address: {address}")
                        
                except Exception as e:
                    self.logger.warning(f"Error extracting item {i+1}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error extracting addresses: {e}")
        
        return addresses
    
    def _extract_address_from_element(self, element) -> Optional[str]:
        """Extract address from a list item element."""
        try:
            # Try multiple selectors for address
            address_selectors = [
                "[data-item-id*='address']",
                "[aria-label*='Address']",
                "[data-tooltip*='Address']",
                "span[aria-label*='Address']",
                "div[aria-label*='Address']"
            ]
            
            for selector in address_selectors:
                address = self._safe_extract_text(element, selector)
                if address:
                    return address
            
            # If no specific address selector works, try to find any text that looks like an address
            all_text = element.text
            lines = all_text.split('\n')
            
            # Look for lines that might be addresses (contain street numbers, common address words)
            for line in lines:
                line = line.strip()
                if (line and 
                    any(char.isdigit() for char in line) and  # Contains numbers
                    any(word in line.lower() for word in ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr', 'lane', 'ln', 'way', 'place', 'pl', 'court', 'ct', 'blvd', 'boulevard'])):
                    return line
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error extracting address: {e}")
            return None
    
    def _extract_name_from_element(self, element) -> Optional[str]:
        """Extract name from a list item element."""
        try:
            name_selectors = [
                "h3",
                "[aria-label*='Title']",
                "[data-tooltip]",
                "span[aria-label*='Title']"
            ]
            
            for selector in name_selectors:
                name = self._safe_extract_text(element, selector)
                if name:
                    return name
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error extracting name: {e}")
            return None
    
    def _safe_extract_text(self, element, selector: str) -> Optional[str]:
        """Safely extract text from an element using a CSS selector."""
        try:
            found_element = element.find_element(By.CSS_SELECTOR, selector)
            return found_element.text.strip()
        except NoSuchElementException:
            return None
    
    def save_to_csv(self, addresses: List[AddressItem], filename: str):
        """Save addresses to a CSV file."""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'address'])
            
            for item in addresses:
                writer.writerow([item.name or '', item.address])
        
        self.logger.info(f"Saved {len(addresses)} addresses to {filename}")


def extract_addresses_from_javascript(page_source):
    """
    Extract addresses from embedded JavaScript data in the page source.
    Google Maps stores the full address list in JavaScript structures.
    """
    addresses = set()
    logger.info("Extracting addresses from JavaScript data...")
    
    # Multiple regex patterns to extract address data from JavaScript
    patterns = [
        # Pattern for complete addresses with street number, direction, street name, and street type
        r'"([0-9]+\s+(?:SW|NW|NE|SE|N|S|E|W|North|South|East|West)?\s*[^,"]*(?:St|Street|Dr|Drive|Rd|Road|Ave|Avenue|Ct|Court|Cir|Circle|Ter|Terrace|Pl|Place|Way|Ln|Lane|Blvd|Boulevard)[^,"]*(?:,\s*[^,"]+)*(?:,\s*[A-Z]{2})?\s*(?:\d{5})?[^"]*)"',
        
        # Pattern for addresses in array format  
        r'\["([0-9]+\s+(?:SW|NW|NE|SE|N|S|E|W)?\s*[^"]*(?:St|Street|Dr|Drive|Rd|Road|Ave|Avenue|Ct|Court|Cir|Circle|Ter|Terrace|Pl|Place|Way|Ln|Lane|Blvd|Boulevard)[^"]*)"',
        
        # Pattern for addresses with USA suffix
        r'"([0-9]+\s+(?:SW|NW|NE|SE|N|S|E|W)?\s*[^"]*(?:St|Street|Dr|Drive|Rd|Road|Ave|Avenue|Ct|Court|Cir|Circle|Ter|Terrace|Pl|Place|Way|Ln|Lane|Blvd|Boulevard)[^"]*,\s*[^"]*,\s*[A-Z]{2}\s*\d{5}[^"]*)"',
        
        # Pattern for addresses in title or name fields
        r'(?:title|name|address)["\']\s*:\s*["\']([0-9]+\s+(?:SW|NW|NE|SE|N|S|E|W)?\s*[^"\']*(?:St|Street|Dr|Drive|Rd|Road|Ave|Avenue|Ct|Court|Cir|Circle|Ter|Terrace|Pl|Place|Way|Ln|Lane|Blvd|Boulevard)[^"\']*)["\']',
        
        # Pattern for addresses in JSON-like structures
        r'(?:address|location)["\']\s*:\s*["\']([0-9]+\s+(?:SW|NW|NE|SE|N|S|E|W)?\s*[^"\']*(?:St|Street|Dr|Drive|Rd|Road|Ave|Avenue|Ct|Court|Cir|Circle|Ter|Terrace|Pl|Place|Way|Ln|Lane|Blvd|Boulevard)[^"\']*)["\']',
        
        # Pattern for standalone street addresses
        r'"([0-9]+\s+(?:SW|NW|NE|SE|N|S|E|W)?\s*[^"]*(?:St|Street|Dr|Drive|Rd|Road|Ave|Avenue|Ct|Court|Cir|Circle|Ter|Terrace|Pl|Place|Way|Ln|Lane|Blvd|Boulevard)[^"]*)"',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, page_source, re.IGNORECASE)
        logger.info(f"Pattern found {len(matches)} matches")
        
        for match in matches:
            address = match.strip()
            
            # Clean up and validate the address
            if len(address) > 10 and any(keyword in address.lower() for keyword in ['rd', 'dr', 'st', 'ave', 'ct', 'cir', 'ter', 'pl', 'way', 'ln', 'blvd', 'street', 'drive', 'road', 'avenue', 'court', 'circle', 'terrace', 'place', 'lane', 'boulevard']):
                # Remove any trailing commas or quotes
                address = re.sub(r'[",\s]+$', '', address)
                addresses.add(address)
    
    # Additional extraction: Look for data structures containing multiple addresses
    # Search for arrays or objects that might contain address lists
    array_patterns = [
        r'\[\s*(?:\[[^\]]*"([0-9]+\s+(?:SW|NW|NE|SE|N|S|E|W)\s+[^"]*(?:Rd|Dr|St|Ave|Ct|Cir|Ter|Pl|Way|Ln|Blvd)[^"]*)"[^\]]*\],?\s*)+\]',
        r'(?:places|locations|addresses|items)\s*[:=]\s*\[[^\]]*"([0-9]+\s+(?:SW|NW|NE|SE|N|S|E|W)\s+[^"]*(?:Rd|Dr|St|Ave|Ct|Cir|Ter|Pl|Way|Ln|Blvd)[^"]*)"',
    ]
    
    for pattern in array_patterns:
        matches = re.findall(pattern, page_source, re.IGNORECASE | re.DOTALL)
        logger.info(f"Array pattern found {len(matches)} matches")
        for match in matches:
            address = match.strip()
            if len(address) > 10 and any(keyword in address.lower() for keyword in ['rd', 'dr', 'st', 'ave', 'ct', 'cir', 'ter', 'pl', 'way', 'ln', 'blvd', 'street', 'drive', 'road', 'avenue', 'court', 'circle', 'terrace', 'place', 'lane', 'boulevard']):
                addresses.add(address)
    
    logger.info(f"JavaScript extraction found {len(addresses)} unique addresses")
    return list(addresses)

def enhanced_address_extraction(driver):
    """
    Enhanced address extraction that combines DOM scraping with JavaScript data extraction.
    """
    all_addresses = set()
    
    # 1. Extract from JavaScript data first (this is likely to have the most complete data)
    page_source = driver.page_source
    js_addresses = extract_addresses_from_javascript(page_source)
    all_addresses.update(js_addresses)
    logger.info(f"JavaScript extraction: {len(js_addresses)} addresses")
    
    # 2. Extract from DOM elements (existing method)
    dom_addresses = extract_addresses_from_dom(driver)
    all_addresses.update(dom_addresses)
    logger.info(f"DOM extraction: {len(dom_addresses)} addresses")
    
    # 3. Save debug information
    save_debug_info(driver, page_source, len(all_addresses))
    
    return list(all_addresses)

def extract_addresses_from_dom(driver):
    """
    Extract addresses using the existing DOM-based method.
    """
    addresses = set()
    
    # Multiple CSS selectors to try
    selectors = [
        '.fontHeadlineSmall',  # Address titles
        '[data-value*="Lee\'s Summit"]',  # Data attributes
        '.rZF81c',  # Address text
        '.kHLxzc',  # Address containers
        'button[jsaction*="pane"]',  # Interactive address buttons
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                try:
                    text = element.text.strip()
                    if text and len(text) > 5:
                        # Check if it looks like an address (has street number and street type)
                        if (re.match(r'^\d+\s+', text) and 
                            any(keyword in text.lower() for keyword in ['rd', 'dr', 'st', 'ave', 'ct', 'cir', 'ter', 'pl', 'way', 'ln', 'blvd', 'street', 'drive', 'road', 'avenue', 'court', 'circle', 'terrace', 'place', 'lane', 'boulevard'])):
                            addresses.add(text)
                except:
                    continue
        except:
            continue
    
    return list(addresses)

def save_debug_info(driver, page_source, total_addresses):
    """
    Saves debug information about the current page source and total addresses found.
    This can be useful for analyzing why addresses might be missed.
    """
    logger.info(f"Current Page Source Length: {len(page_source)}")
    logger.info(f"Total Unique Addresses Found: {total_addresses}")
    
    # Debug logging only (debug files removed for cleanup)
    logger.debug("Page source analysis available in logs")


def main():
    """Example usage of the Google Maps List Scraper."""
    # Your specific Google Maps list URL
    list_url = "https://maps.app.goo.gl/qr1Y6sFwU58MU4Sm7"  # Winterset - Longview list (1,192 addresses)
    
    scraper = GoogleMapsListScraper(headless=False)  # Set to True for production
    
    try:
        scraper.start()
        
        # Scrape addresses from the list
        addresses = scraper.scrape_addresses(list_url)
        
        if addresses:
            print(f"Found {len(addresses)} addresses:")
            for i, item in enumerate(addresses, 1):
                print(f"{i}. {item.address}")
                if item.name:
                    print(f"   Name: {item.name}")
                print()
            
            # Save results
            scraper.save_to_csv(addresses, "data/addresses.csv")
        else:
            print("No addresses found in the list.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.stop()


if __name__ == "__main__":
    main() 