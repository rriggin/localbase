#!/usr/bin/env python3
"""
Dynamic Google Maps List Scraper

This scraper handles large lists by scrolling through the entire list to capture all addresses.
It's designed to extract all 1,192 addresses from your "Winterset - Longview" list.
"""

import time
import csv
import re
import logging
from typing import List, Set, Tuple
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@dataclass
class Address:
    """Represents an extracted address."""
    name: str
    address: str
    coordinates: Tuple[float, float] = None

    def __str__(self):
        return f"{self.name}: {self.address}"


class DynamicListScraper:
    """Scraper that can handle dynamic loading of large Google Maps lists."""
    
    def __init__(self, headless: bool = True):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        self.headless = headless
        self.driver = None
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        # Disable images and CSS for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def extract_addresses_from_list(self, url: str, max_scroll_attempts: int = 50) -> List[Address]:
        """
        Extract all addresses from a Google Maps list by scrolling through the entire list.
        
        Args:
            url: Google Maps list URL
            max_scroll_attempts: Maximum number of scroll attempts to avoid infinite loops
            
        Returns:
            List of Address objects
        """
        if not self.driver:
            self.setup_driver()
            
        try:
            self.logger.info(f"Loading Google Maps list: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Try to find the list container
            list_selectors = [
                '[data-value="Saved"]',  # Saved places container
                '.section-listbox',      # List box container
                '[role="main"]',         # Main content area
                '.section-scrollbox'     # Scrollable section
            ]
            
            list_container = None
            for selector in list_selectors:
                try:
                    list_container = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found list container using selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not list_container:
                self.logger.warning("Could not find list container, using document body")
                list_container = self.driver.find_element(By.TAG_NAME, "body")
            
            addresses = self.scroll_and_extract(list_container, max_scroll_attempts)
            
            self.logger.info(f"Successfully extracted {len(addresses)} addresses")
            return addresses
            
        except Exception as e:
            self.logger.error(f"Error extracting addresses: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
    
    def scroll_and_extract(self, container, max_attempts: int) -> List[Address]:
        """
        Scroll through the list and extract all addresses.
        
        Args:
            container: The scrollable container element
            max_attempts: Maximum scroll attempts
            
        Returns:
            List of unique addresses
        """
        addresses = set()  # Use set to avoid duplicates
        last_count = 0
        no_change_count = 0
        
        for attempt in range(max_attempts):
            # Extract addresses from current view
            current_addresses = self.extract_visible_addresses()
            addresses.update(current_addresses)
            
            current_count = len(addresses)
            self.logger.info(f"Scroll attempt {attempt + 1}: Found {current_count} addresses total")
            
            # Check if we found new addresses
            if current_count == last_count:
                no_change_count += 1
                if no_change_count >= 3:  # Stop if no new addresses found in 3 attempts
                    self.logger.info("No new addresses found in last 3 attempts, stopping")
                    break
            else:
                no_change_count = 0
                last_count = current_count
            
            # Scroll down to load more content
            self.driver.execute_script("""
                // Try multiple scroll strategies
                window.scrollTo(0, document.body.scrollHeight);
                
                // Also scroll any scrollable containers
                const containers = document.querySelectorAll('.section-scrollbox, [role="main"], .section-listbox');
                containers.forEach(container => {
                    container.scrollTop = container.scrollHeight;
                });
            """)
            
            # Wait for new content to load
            time.sleep(2)
            
            # Also try pressing Page Down to trigger loading
            if attempt % 5 == 0:  # Every 5th attempt
                try:
                    from selenium.webdriver.common.keys import Keys
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
                    time.sleep(1)
                except:
                    pass
        
        return list(addresses)
    
    def extract_visible_addresses(self) -> Set[Address]:
        """Extract addresses from currently visible elements."""
        addresses = set()
        
        # Multiple selector strategies for finding address elements
        selectors = [
            'a[data-value="Directions"]',  # Direction links
            '.section-result',             # Result items
            '.place-result',              # Place results
            '[data-result-index]',        # Indexed results
            'div[jsaction*="mouseenter"]', # Interactive place divs
            'h3[class*="fontHeadlineSmall"]', # Place names
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    address = self.extract_address_from_element(element)
                    if address:
                        addresses.add(address)
            except Exception as e:
                self.logger.debug(f"Error with selector {selector}: {e}")
        
        # Also try extracting from page source using regex
        page_source = self.driver.page_source
        regex_addresses = self.extract_addresses_from_source(page_source)
        addresses.update(regex_addresses)
        
        return addresses
    
    def extract_address_from_element(self, element) -> Address:
        """Extract address information from a single element."""
        try:
            # Try to get the text content
            text = element.text.strip()
            if not text or len(text) < 5:
                return None
            
            # Try to get href for more info
            href = ""
            try:
                href = element.get_attribute("href") or ""
            except:
                pass
            
            # Extract coordinates from href if available
            coordinates = None
            if href:
                coord_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', href)
                if coord_match:
                    lat, lng = float(coord_match.group(1)), float(coord_match.group(2))
                    coordinates = (lat, lng)
            
            # Clean up the text to extract name and address
            lines = text.split('\n')
            name = lines[0] if lines else text
            address = lines[1] if len(lines) > 1 else ""
            
            # Filter out non-address text
            if any(skip in text.lower() for skip in ['directions', 'website', 'call', 'save']):
                return None
            
            if not address and len(name) > 50:  # Long text might contain address
                # Try to extract address from long name
                address_match = re.search(r'\d+.*(?:St|Street|Ave|Avenue|Dr|Drive|Rd|Road|Blvd|Boulevard|Ct|Court|Cir|Circle|Ln|Lane)', name, re.IGNORECASE)
                if address_match:
                    address = address_match.group(0)
                    name = name.replace(address, '').strip()
            
            if name and (address or coordinates):
                return Address(name=name, address=address, coordinates=coordinates)
                
        except Exception as e:
            self.logger.debug(f"Error extracting from element: {e}")
        
        return None
    
    def extract_addresses_from_source(self, page_source: str) -> Set[Address]:
        """Extract addresses from page source using regex patterns."""
        addresses = set()
        
        # Look for address patterns in the source
        patterns = [
            r'"([^"]*\d+[^"]*(?:St|Street|Ave|Avenue|Dr|Drive|Rd|Road|Blvd|Boulevard|Ct|Court|Cir|Circle|Ln|Lane)[^"]*)"',
            r'"([^"]*Lee\'s Summit[^"]*)"',
            r'"([^"]*MO 64081[^"]*)"',
            r'"([^"]*SW [^"]*)"',  # Southwest addresses common in Lee's Summit
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            for match in matches:
                if len(match) > 10 and len(match) < 200:  # Reasonable address length
                    address = Address(name=match, address=match)
                    addresses.add(address)
        
        return addresses
    
    def save_to_csv(self, addresses: List[Address], filename: str):
        """Save addresses to CSV file."""
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Address', 'Latitude', 'Longitude'])
            
            for addr in addresses:
                lat, lng = addr.coordinates if addr.coordinates else ('', '')
                writer.writerow([addr.name, addr.address, lat, lng])
        
        self.logger.info(f"Saved {len(addresses)} addresses to {filename}")


def main():
    """Main function to run the dynamic scraper."""
    url = "https://maps.app.goo.gl/bT85WjFbSkNDmRYH9"
    
    print("=== Dynamic Google Maps List Scraper ===")
    print(f"Target URL: {url}")
    print("This scraper will scroll through the entire list to capture all addresses.")
    print("Expected: ~1,192 addresses from 'Winterset - Longview' list")
    print()
    
    scraper = DynamicListScraper(headless=False)  # Set to False to watch the process
    
    try:
        addresses = scraper.extract_addresses_from_list(url, max_scroll_attempts=100)
        
        if addresses:
            output_file = "data/winterset_longview_dynamic_extracted.csv"
            scraper.save_to_csv(addresses, output_file)
            
            print(f"\n✅ SUCCESS! Extracted {len(addresses)} addresses")
            print(f"📁 Saved to: {output_file}")
            
            # Show preview
            print("\n📋 Preview of extracted addresses:")
            for i, addr in enumerate(addresses[:10]):
                print(f"{i+1:2d}. {addr}")
            
            if len(addresses) > 10:
                print(f"... and {len(addresses) - 10} more addresses")
            
            if len(addresses) >= 1000:
                print("\n🎉 Excellent! Successfully captured large dataset!")
            elif len(addresses) > 500:
                print(f"\n✅ Good progress! Got {len(addresses)} addresses (more than static scraping)")
            else:
                print(f"\n⚠️  Only got {len(addresses)} addresses. May need to adjust scraping strategy.")
                
        else:
            print("❌ No addresses found. The scraping strategy may need adjustment.")
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 