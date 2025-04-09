import os
import json
import re
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from pydantic import BaseModel
import requests
import time
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
import random

# Configure API keys
genai.configure(api_key="AIzaSyAyrlxTyIIWzk97zTBtaZAf6nr7naoyFVY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "fdf46e3b3848b7182af27b84f4c0c24e35e7a6936ca95fda2c2050fff3962208")  # Replace with your actual key

class SearchQuery(BaseModel):
    query: str
    channel: str

class SearchResult(BaseModel):
    company_name: str
    contact_info: Optional[str] = None
    channel_id: int
    confidence_score: float
    source: Optional[str] = None
    source_link: Optional[str] = None
    employee_count: Optional[int] = None
    industry: Optional[str] = None
    location: Optional[str] = None

from typing import List
import time
import json
from serpapi import GoogleSearch  # Assuming you're using SerpAPI

def google_search_by_channel(query: str, channel: str, num_results: int = 10) -> List[str]:
    """Search for prospects based on the specified channel"""
    try:
        site_filter = ""
        keywords = '(looking for a solution for OR need help with OR can anyone recommend OR alternative to OR struggling with OR how do you handle)'

        # Configure channel-specific search parameters
        if channel.lower() == "linkedin":
            site_filter = "site:linkedin.com"
            search_query = f'{site_filter} {keywords} {query} posts'
        elif channel.lower() == "twitter":
            site_filter = "site:twitter.com"
            search_query = f'{site_filter} {keywords} {query} -filter:links -filter:retweets posts'
        elif channel.lower() == "reddit":
            site_filter = "site:reddit.com"
            search_query = f'{site_filter} {keywords} {query} posts'
        elif channel.lower() == "quora":
            site_filter = "site:quora.com"
            search_query = f'{site_filter} {keywords} {query} posts'
        else:
            # Default search without site restriction
            search_query = f'{query} {keywords}'

        all_urls = []
        page = 0

        while len(all_urls) < num_results:
            search = GoogleSearch({
                "q": search_query,
                "engine": "google",
                "api_key": SERPAPI_KEY,
                "num": min(50, num_results - len(all_urls)),  # Request up to 50 results per page
                "start": page * 50,  # Pagination offset
                "gl": "us"  # Search in English
            })

            results = search.get_dict()
            print("Query:", search_query)
            # print("Raw API Response:", json.dumps(results, indent=2))  # Debugging

            if "organic_results" not in results or not results["organic_results"]:
                break

            for result in results["organic_results"]:
                if "link" in result:
                    url = result["link"].split("?")[0].strip()

                    # Apply channel-specific URL filtering
                    if channel.lower() == "linkedin" and "linkedin.com" in url:
                        if any(x in url.lower() for x in ['/posts/', '/in/', '/pulse/', '/activity/']):
                            all_urls.append(url)
                    elif channel.lower() == "twitter" and "twitter.com" in url:
                        all_urls.append(url)
                    elif channel.lower() == "reddit" and "reddit.com" in url:
                        if any(x in url.lower() for x in ['/r/', '/comments/']):
                            all_urls.append(url)
                    elif channel.lower() == "quora" and "quora.com" in url:
                        all_urls.append(url)
                    elif channel.lower() not in ["linkedin", "twitter", "reddit", "quora"]:
                        all_urls.append(url)

                    if len(all_urls) >= num_results:
                        break

            page += 1
            time.sleep(2)  # Avoid hitting rate limits

        # print("All URLs:", all_urls)
        return all_urls[:num_results]

    except Exception as e:
        print(f"Error in {channel} search: {e}")
        return []


def extract_content_by_channel(url: str, channel: str) -> Optional[Dict]:
    """Extract content based on the channel"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract metadata common to all channels
        meta_tags = soup.find_all('meta')
        meta_data = {tag.get('property', tag.get('name')): tag.get('content') 
                    for tag in meta_tags if tag.get('content')}
        
        content = meta_data.get('og:description', '') or meta_data.get('description', '')
        title = meta_data.get('og:title', '') or meta_data.get('title', '')
        
        result = {
            'url': url,
            'content': content,
            'title': title,
            'post_date': meta_data.get('article:published_time', time.strftime("%Y-%m-%d")),
        }
        
        # Channel-specific extraction
        if channel.lower() == "linkedin":
            company_info = {}
            if '/company/' in url:
                company_info = {
                    'name': meta_data.get('og:title', '').split('|')[0].strip(),
                    'industry': next((tag.get('content') for tag in meta_tags 
                                    if tag.get('name') == 'industry'), None),
                    'size': next((tag.get('content') for tag in meta_tags 
                                if tag.get('name') == 'company-size'), None),
                    'location': next((tag.get('content') for tag in meta_tags 
                                    if tag.get('name') == 'location'), None)
                }
            
            profile_info = {}
            if '/in/' in url:
                profile_info = {
                    'name': title.split('-')[0].strip() if '-' in title else title,
                    'role': title.split('-')[1].strip() if '-' in title else '',
                    'company': title.split('at')[-1].strip() if 'at' in title else ''
                }
            
            result.update({
                'company_info': company_info,
                'profile_info': profile_info
            })
            
        elif channel.lower() == "twitter":
            tweet_info = {
                'username': soup.select_one('a[href*="/status/"]')['href'].split('/')[1] if soup.select_one('a[href*="/status/"]') else '',
                'followers': meta_data.get('profile:followers_count', ''),
                'verified': bool(soup.select_one('svg[aria-label="Verified Account"]'))
            }
            result.update({'tweet_info': tweet_info})
            
        elif channel.lower() == "reddit":
            subreddit = url.split('/r/')[-1].split('/')[0] if '/r/' in url else ''
            result.update({
                'subreddit': subreddit,
                'score': meta_data.get('score', 0),
                'num_comments': meta_data.get('num_comments', 0)
            })
        
        return result
        
    except Exception as e:
        print(f"Error extracting {channel} content from {url}: {e}")
        return None

def analyze_with_gemini(post_info: Dict, query: str, channel: str) -> Dict[str, Any]:
    """Enhanced analysis for different content channels using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Customize the analysis prompt based on the channel
        if channel.lower() == 'linkedin':
            analysis_prompt = f"""
            Analyze this LinkedIn post to identify potential sales leads. Return ONLY a JSON object with no additional text.

            ### **Post Details:**
            - **Content:** {post_info.get('content', '')}
            - **Title:** {post_info.get('title', '')}
            - **Company Info:** {post_info.get('company_info', {})}
            - **Profile Info:** {post_info.get('profile_info', {})}

            ### **Criteria for a Valid Lead (Strict Filtering):**
            ✅ **The post must be written by an individual (not company news, documentation, or generic updates).**  
            ✅ **The post must discuss a challenge, frustration, or need related to:** "{query}".  
            ✅ **Exclude posts that are just sharing industry news, technical documentation, or self-promotions.**  
            ✅ **Prioritize posts with direct buying signals (e.g., asking for recommendations, looking for a solution, discussing pain points).**  

            ### **Return JSON with These Exact Fields:**
            ```json
            {{
                "is_potential_lead": (true/false),  
                "intent_score": (number between 0-1),  
                "decision_maker_score": (number between 0-1),  
                "urgency_score": (number between 0-1),  
                "relevance_score": (number between 0-1),  
                "overall_confidence": (number between 0-1),  
                "key_insights": ["insight1", "insight2", ...]  
            }}
            """

        elif channel.lower() == 'twitter':
            analysis_prompt = f"""
            Analyze this Twitter post for sales opportunities and return ONLY a JSON object with no additional text:
            Tweet: {post_info.get('tweet_text', '')}
            User Info: {post_info.get('user_info', {})}
            
            Consider:
            1. Buying intent signals
            2. Pain points mentioned
            3. Decision-maker status
            4. Relevance to the product/service: {query}
            
            Return ONLY a JSON object with these exact fields:
            {{
                "intent_score": (number between 0-1),
                "decision_maker_score": (number between 0-1),
                "urgency_score": (number between 0-1),
                "relevance_score": (number between 0-1),
                "overall_confidence": (number between 0-1),
                "key_insights": ["insight1", "insight2", ...]
            }}
            """
        elif channel.lower() == 'reddit':
            analysis_prompt = f"""
            Analyze this Reddit post for sales opportunities and return ONLY a JSON object with no additional text:
            Post Content: {post_info.get('content', '')}
            Subreddit: {post_info.get('subreddit', '')}
            
            Consider:
            1. Buying intent signals
            2. Pain points mentioned
            3. Decision-maker status
            4. Relevance to the product/service: {query}
            
            Return ONLY a JSON object with these exact fields:
            {{
                "intent_score": (number between 0-1),
                "decision_maker_score": (number between 0-1),
                "urgency_score": (number between 0-1),
                "relevance_score": (number between 0-1),
                "overall_confidence": (number between 0-1),
                "key_insights": ["insight1", "insight2", ...]
            }}
            """
        else:
            analysis_prompt = f"""
            Analyze this content for sales opportunities and return ONLY a JSON object with no additional text:
            Content: {post_info.get('content', '')}
            Title: {post_info.get('title', '')}
            
            Consider:
            1. Buying intent signals
            2. Pain points mentioned
            3. Decision-maker status
            4. Relevance to the product/service: {query}
            
            Return ONLY a JSON object with these exact fields:
            {{
                "intent_score": (number between 0-1),
                "decision_maker_score": (number between 0-1),
                "urgency_score": (number between 0-1),
                "relevance_score": (number between 0-1),
                "overall_confidence": (number between 0-1),
                "key_insights": ["insight1", "insight2", ...]
            }}
            """
        
        # Generate the content analysis using Gemini AI model
        response = model.generate_content(analysis_prompt)
        response_text = response.text.strip()
        
        # Clean up the response to ensure valid JSON
        response_text = re.sub(r'```json\s*|\s*```', '', response_text)
        response_text = response_text.strip()
        
        # Parse the response into JSON
        try:
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group(0))
            else:
                raise ValueError("Could not extract valid JSON from response")
        
        # Ensure all required fields are present with valid values
        default_analysis = {
            'intent_score': 0.0,
            'decision_maker_score': 0.0,
            'urgency_score': 0.0,
            'relevance_score': 0.0,
            'overall_confidence': 0.0,
            'key_insights': []
        }
        
        for key in default_analysis:
            if key not in analysis:
                analysis[key] = default_analysis[key]
            elif key.endswith('_score') or key == 'overall_confidence':
                try:
                    analysis[key] = float(analysis[key])
                    analysis[key] = max(0.0, min(1.0, analysis[key]))
                except (ValueError, TypeError):
                    analysis[key] = default_analysis[key]
            elif key == 'key_insights' and not isinstance(analysis[key], list):
                analysis[key] = default_analysis[key]
        
        return analysis
    
    except Exception as e:
        print(f"Error in Gemini analysis: {e}")
        return {
            'intent_score': 0.0,
            'decision_maker_score': 0.0,
            'urgency_score': 0.0,
            'relevance_score': 0.0,
            'overall_confidence': 0.0,
            'key_insights': []
        }


def search_prospects(query: str, channel: str, channel_id: int) -> List[SearchResult]:
    """Enhanced prospect search with improved filtering and scoring"""
    urls = google_search_by_channel(query, channel)
    results = []  # Initialize the list to store results
    
    for url in urls:
        content_info = extract_content_by_channel(url, channel)
        print("\ncontent_info", content_info)
        if not content_info:
            continue
            
        analysis = analyze_with_gemini(content_info, query, channel)
        
        # Calculate weighted confidence score
        confidence_score = (
            analysis['intent_score'] * 0.35 +
            analysis['decision_maker_score'] * 0.25 +
            analysis['urgency_score'] * 0.20 +
            analysis['relevance_score'] * 0.20
        )
        
        # Extract company/user information based on channel
        if channel.lower() == "linkedin":
            company_info = content_info.get('company_info', {})
            profile_info = content_info.get('profile_info', {})
            
            company_name = (company_info.get('name') or 
                          profile_info.get('company') or 
                          'Unknown Company')
            contact_info = profile_info.get('name')
            employee_count = _parse_employee_count(company_info.get('size'))
            industry = company_info.get('industry')
            location = company_info.get('location')
            
        elif channel.lower() == "twitter":
            tweet_info = content_info.get('tweet_info', {})
            company_name = tweet_info.get('username', 'Unknown User')
            contact_info = f"@{tweet_info.get('username')}" if tweet_info.get('username') else None
            employee_count = None
            industry = None
            location = None
            
        elif channel.lower() == "reddit":
            company_name = f"Reddit user in r/{content_info.get('subreddit', 'Unknown')}"
            contact_info = None
            employee_count = None
            industry = content_info.get('subreddit')
            location = None
            
        else:
            company_name = content_info.get('title', 'Unknown Source')
            contact_info = None
            employee_count = None
            industry = None
            location = None
        
        # Create search result
        result = SearchResult(
            company_name=company_name,
            contact_info=contact_info,
            channel_id=channel_id,
            confidence_score=round(confidence_score, 2),
            source=channel.capitalize(),
            source_link=url,
            employee_count=employee_count,
            industry=industry,
            location=location
        )

        results.append(result)

        # Only include results with sufficient confidence
        # if confidence_score >= 0.4:  # Minimum threshold for quality leads
        #     print(f"Sorted results for {query}: {results}")
        #     results.append(result)
    
    # Sort results by confidence score
    results.sort(key=lambda x: x.confidence_score, reverse=True)
    print(f"Sorted results for {query}: {results}")
    return results  # Return the list of results


def _parse_employee_count(size_str: Optional[str]) -> Optional[int]:
    """Helper function to parse LinkedIn company size strings"""
    if not size_str:
        return None
        
    try:
        # Handle ranges like "51-200 employees"
        if '-' in size_str:
            lower, upper = size_str.split('-')
            return int(upper.split()[0])  # Take the upper bound
        # Handle "10000+ employees"
        elif '+' in size_str:
            return int(size_str.split('+')[0])
        # Handle direct numbers
        return int(''.join(filter(str.isdigit, size_str)))
    except:
        return None

def generate_mock_results(query: str, channel: str, channel_id: int) -> List[SearchResult]:
    """Generate mock search results focusing on companies with active needs"""
    
    words = query.split()
    main_term = words[0] if words else "Tech"
    
    results = [
        SearchResult(
            company_name=f"{main_term} Solutions Inc.",
            contact_info=f"s.chen@{main_term.lower()}solutions.com",
            channel_id=channel_id,
            confidence_score=0.95,
            source="LinkedIn",
            source_link=f"https://linkedin.com/posts/schen_{random.randint(10000, 99999)}",
            employee_count=1000,
            industry="Software",
            location="San Francisco, CA"
        ),
        SearchResult(
            company_name=f"{main_term} Technologies",
            contact_info=f"mike.j@{main_term.lower()}tech.com",
            channel_id=channel_id,
            confidence_score=0.85,
            source="LinkedIn",
            source_link=f"https://linkedin.com/posts/mjohnson_{random.randint(10000, 99999)}",
            employee_count=500,
            industry="IT Services",
            location="New York, NY"
        ),
        SearchResult(
            company_name=f"Global {main_term}",
            contact_info=f"l.wong@global{main_term.lower()}.com",
            channel_id=channel_id,
            confidence_score=0.75,
            source="LinkedIn",
            source_link=f"https://linkedin.com/posts/lwong_{random.randint(10000, 99999)}",
            employee_count=2000,
            industry="Finance",
            location="London, UK"
        )
    ]
    
    return results