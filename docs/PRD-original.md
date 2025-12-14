# Product Requirements Document (PRD)
# Space Weather Report Automation System

**Version:** 1.0
**Date:** November 2, 2025
**Status:** Production
**Author:** System Analysis

---

## Executive Summary

The Space Weather Report Automation System is a production-ready, AI-powered platform that automatically generates comprehensive space weather reports from authoritative scientific sources. The system fetches data from NOAA SWPC, UK Met Office, and other reliable sources every 6 hours, uses Claude AI to generate professional reports in natural language, and saves them in multiple formats directly to an Obsidian vault for knowledge management integration.

**Current Status:** Fully operational with 100% success rate on recent runs
**Last Deployment:** November 2, 2025
**Operational Uptime:** Continuous 6-hour automated execution

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Target Users](#2-target-users)
3. [User Stories](#3-user-stories)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [System Architecture](#6-system-architecture)
7. [Data Sources](#7-data-sources)
8. [AI Integration](#8-ai-integration)
9. [Output Formats](#9-output-formats)
10. [Automation & Scheduling](#10-automation--scheduling)
11. [Configuration Management](#11-configuration-management)
12. [Error Handling & Resilience](#12-error-handling--resilience)
13. [Logging & Monitoring](#13-logging--monitoring)
14. [Security & Privacy](#14-security--privacy)
15. [Future Enhancements](#15-future-enhancements)
16. [Success Metrics](#16-success-metrics)
17. [Technical Specifications](#17-technical-specifications)
18. [Deployment & Operations](#18-deployment--operations)

---

## 1. Product Overview

### 1.1 Vision

To provide space weather enthusiasts, researchers, and amateur astronomers with automated, professional-grade space weather reports that synthesize information from multiple authoritative sources into easy-to-understand summaries, delivered automatically and integrated seamlessly with personal knowledge management systems.

### 1.2 Mission

Democratize access to space weather information by automating the collection, analysis, and presentation of solar activity data, making it accessible to anyone interested in solar flares, geomagnetic storms, and aurora activity.

### 1.3 Value Proposition

**For Space Weather Enthusiasts:**
- Automatic daily reports without manual effort
- Professional-quality analysis comparable to official forecasts
- Educational links for learning about solar phenomena
- Historical archive for trend analysis

**For Obsidian Users:**
- Seamless integration with personal knowledge vault
- Markdown format for easy linking and searching
- Timestamped reports for chronological organization
- Can reference in daily notes and projects

**For Researchers:**
- Multi-source data aggregation in one place
- Structured JSON format for data analysis
- Reliable automated collection
- 30-day historical archive

**For Aurora Chasers:**
- Geomagnetic storm forecasts
- Kp index tracking
- CME impact predictions
- Multiple-day outlook

### 1.4 Key Features

1. **Multi-Source Data Fetching** - Aggregates from 5+ authoritative sources
2. **AI-Powered Report Generation** - Uses Claude Sonnet 4 for professional natural language reports
3. **Multiple Output Formats** - HTML, Markdown, JSON, and plain text
4. **Automated Scheduling** - Runs every 6 hours via launchd service
5. **Obsidian Vault Integration** - Direct save to knowledge management system
6. **Comprehensive Error Handling** - Resilient to individual source failures
7. **Browser MCP Integration** - Infrastructure for bypassing robots.txt restrictions
8. **Automatic Archiving** - 30-day retention with automatic cleanup
9. **Professional Linking** - 15+ types of educational resource links
10. **Fallback Templates** - Ensures reports even if AI unavailable

---

## 2. Target Users

### 2.1 Primary Users

**Space Weather Enthusiasts**
- **Demographics:** Adults 25-65, tech-savvy
- **Goals:** Stay informed about solar activity
- **Pain Points:** Manual checking of multiple sources is time-consuming
- **Frequency:** Daily to multiple times per day

**Amateur Astronomers**
- **Demographics:** Adults 30-70, hobbyist to serious
- **Goals:** Plan observing sessions around solar activity
- **Pain Points:** Need consolidated information for planning
- **Frequency:** Weekly to daily

**Aurora Photographers**
- **Demographics:** Adults 25-55, photography enthusiasts
- **Goals:** Predict aurora opportunities for photography
- **Pain Points:** Missing opportunities due to lack of timely forecasts
- **Frequency:** Daily during aurora season

**Obsidian Power Users**
- **Demographics:** Adults 25-50, knowledge workers
- **Goals:** Integrate space weather into personal knowledge management
- **Pain Points:** Manual capture and linking is tedious
- **Frequency:** Multiple times per day (for vault access)

### 2.2 Secondary Users

**Researchers & Students**
- **Use Case:** Space weather research, solar physics studies
- **Needs:** Historical data, structured formats, reliable sources

**Radio Operators (Ham Radio)**
- **Use Case:** HF propagation forecasting
- **Needs:** Solar flare information, radio blackout predictions

**Satellite Operators (Personal/Educational)**
- **Use Case:** CubeSat operations, educational projects
- **Needs:** Geomagnetic activity forecasts, CME warnings

---

## 3. User Stories

### 3.1 Core User Stories

**US-001: Automated Report Generation**
- **As a** space weather enthusiast
- **I want** automated daily reports generated every 6 hours
- **So that** I can stay informed without manual effort
- **Acceptance Criteria:**
  - System runs automatically every 6 hours
  - Reports generated within 60 seconds
  - No manual intervention required
  - Notifications only on failures

**US-002: Multi-Format Output**
- **As an** Obsidian user
- **I want** reports saved in Markdown format
- **So that** I can integrate them with my knowledge vault
- **Acceptance Criteria:**
  - Markdown format is Obsidian-compatible
  - Files saved to configurable vault directory
  - Proper frontmatter for metadata
  - Internal linking structure preserved

**US-003: Professional Report Quality**
- **As a** researcher
- **I want** comprehensive, well-formatted reports
- **So that** I can rely on them for professional purposes
- **Acceptance Criteria:**
  - Reports include all major solar events
  - Specific times in UTC with sources
  - Active region numbers and classifications
  - Educational links to explanatory resources

**US-004: Reliable Data Collection**
- **As an** aurora photographer
- **I want** reliable geomagnetic forecasts
- **So that** I can plan photography sessions
- **Acceptance Criteria:**
  - System fetches from multiple authoritative sources
  - Continues operation if one source fails
  - Provides 3-day forecast outlook
  - Includes Kp index predictions

**US-005: Historical Archive**
- **As a** student researcher
- **I want** access to historical reports
- **So that** I can analyze trends over time
- **Acceptance Criteria:**
  - Reports retained for 30 days minimum
  - Consistent naming convention for sorting
  - JSON format available for data analysis
  - Automatic cleanup of old files

### 3.2 Advanced User Stories

**US-006: Browser Automation Fallback**
- **As a** system administrator
- **I want** automatic fallback to browser automation for blocked sites
- **So that** reports remain comprehensive even when some sources block scraping
- **Acceptance Criteria:**
  - System detects HTTP 403 / robots.txt blocks
  - Creates browser automation requests
  - Integrates browser-fetched data seamlessly
  - Logs which sites required browser automation

**US-007: Customizable Sources**
- **As a** power user
- **I want** to configure which data sources are used
- **So that** I can prioritize my preferred sources
- **Acceptance Criteria:**
  - YAML configuration for all sources
  - Easy addition of new sources
  - Priority ordering supported
  - Can disable individual sources

**US-008: Alert Notifications**
- **As an** aurora chaser
- **I want** notifications for significant events
- **So that** I don't miss major aurora opportunities
- **Acceptance Criteria:**
  - Configurable thresholds (M-class flares, G2+ storms)
  - Multiple notification methods (email, push)
  - Event-specific messages
  - No false positives

---

## 4. Functional Requirements

### 4.1 Data Collection (FR-DC)

**FR-DC-001: Multi-Source Fetching**
- System MUST fetch data from at least 5 configured sources
- System MUST support HTTP/HTTPS requests with 30-second timeout
- System MUST handle rate limiting gracefully
- System MUST log all fetch attempts with success/failure status

**FR-DC-002: Primary Sources**
- System MUST fetch NOAA SWPC Discussion as primary source
- System MUST fetch UK Met Office Space Weather forecast
- System MUST prioritize primary sources over alternatives

**FR-DC-003: Alternative Sources**
- System MUST attempt alternative sources if primary sources fail
- System MUST support configurable alternative source list
- System MAY use alternative sources for additional context

**FR-DC-004: Data Validation**
- System MUST validate fetched data is not empty
- System MUST check content length is reasonable (>100 bytes)
- System MUST detect error pages vs. actual content
- System SHOULD validate data freshness where timestamps available

**FR-DC-005: Browser Automation Fallback**
- System MAY detect robots.txt blocks (HTTP 403)
- System MAY create browser automation requests for blocked sites
- System MAY integrate Browser MCP workflow
- System MUST log browser automation usage

### 4.2 Report Generation (FR-RG)

**FR-RG-001: AI-Powered Generation**
- System MUST use Claude API for report generation when API key available
- System MUST construct comprehensive prompt with all fetched data
- System MUST include detailed structure requirements in prompt
- System MUST specify linking requirements and style guide

**FR-RG-002: Report Structure**
- Reports MUST include headline with date range
- Reports MUST include opening narrative paragraph
- Reports MUST include flare activity section
- Reports MUST include sunspot regions section
- Reports MUST include CME activity section
- Reports MUST include solar wind parameters
- Reports MUST include geomagnetic conditions
- Reports MUST include 3-day forecast section

**FR-RG-003: Technical Details**
- Reports MUST include specific UTC times for all events
- Reports MUST include active region numbers (AR####)
- Reports MUST include magnetic classifications
- Reports MUST include flare classes and values
- Reports MUST include Kp indices and G-scale ratings
- Reports MUST include solar wind speed and IMF Bz

**FR-RG-004: Educational Linking**
- Reports MUST link UTC times to time zone explanation
- Reports MUST link solar flare classes to explanatory articles
- Reports MUST link NOAA scales to official documentation
- Reports MUST link CMEs to educational resources
- Reports MUST link magnetic classifications to references
- Reports SHOULD include 15+ different link types

**FR-RG-005: Fallback Templates**
- System MUST provide basic template reports if Claude API fails
- Templates MUST include all fetched data
- Templates MUST be properly formatted in all output formats
- Templates MUST be clearly marked as fallback (not AI-generated)

### 4.3 Output Formats (FR-OF)

**FR-OF-001: HTML Format**
- System MUST generate valid HTML5
- HTML MUST include proper semantic tags (h3, h4, ul, li, p, a)
- HTML MUST include proper link attributes (target="_blank" rel="noopener")
- HTML MUST be readable without CSS
- HTML file size SHOULD be 1-8 KB

**FR-OF-002: Markdown Format**
- System MUST generate GitHub-flavored Markdown
- Markdown MUST be Obsidian-compatible
- Markdown MUST convert all HTML links to Markdown link format
- Markdown MUST preserve heading hierarchy
- Markdown file size SHOULD be 1-5 KB

**FR-OF-003: JSON Format**
- System MUST generate valid JSON
- JSON MUST include timestamp field (ISO 8601)
- JSON MUST include all source data fields
- JSON MUST include generated_with field
- JSON MUST be pretty-printed for readability
- JSON file size MAY be larger (~470 KB typical)

**FR-OF-004: Plain Text Format**
- System MUST generate plain text format
- Text MUST strip all HTML tags
- Text MUST preserve line breaks and structure
- Text MUST be readable in any text editor
- Text file size SHOULD be 1-3 KB

**FR-OF-005: Format Selection**
- System MUST support enabling/disabling each format individually
- System MUST generate all enabled formats in single run
- System MUST use consistent filename pattern across formats
- System MUST save all formats to same directory

### 4.4 File Management (FR-FM)

**FR-FM-001: File Naming**
- System MUST use pattern: `space_weather_YYYY-MM-DD_HHMM.{ext}`
- System MUST use UTC time for filename timestamps
- System MUST support configurable filename pattern
- System MUST ensure unique filenames (no overwrites)

**FR-FM-002: File Saving**
- System MUST save files to configurable base directory
- System MUST create directory if it doesn't exist
- System MUST handle file write errors gracefully
- System MUST confirm successful saves in logs

**FR-FM-003: Archive Management**
- System MUST automatically delete files older than configured retention period
- System MUST default to 30-day retention
- System MUST log cleanup operations
- System MUST handle cleanup errors without failing report generation

**FR-FM-004: File Permissions**
- System SHOULD set readable file permissions (644)
- System SHOULD preserve ownership
- System MUST be compatible with Obsidian file monitoring

### 4.5 Automation & Scheduling (FR-AS)

**FR-AS-001: Scheduled Execution**
- System MUST support interval-based scheduling (e.g., every 6 hours)
- System MAY support time-based scheduling (e.g., specific times)
- System MUST execute automatically without user intervention
- System MUST run at configured intervals reliably

**FR-AS-002: launchd Integration (macOS)**
- System MUST provide setup script for launchd service
- System MUST create valid launchd plist file
- System MUST support RunAtLoad for execution at login
- System MUST redirect logs to accessible files

**FR-AS-003: Alternative Scheduling**
- System MUST provide Python-based scheduler as alternative
- System MUST support foreground execution mode
- System MUST allow manual on-demand execution
- System SHOULD provide progress indicators in foreground mode

**FR-AS-004: Execution Reliability**
- System MUST complete execution within 2 minutes maximum
- System MUST recover from transient errors
- System MUST not require manual intervention for common issues
- System SHOULD execute successfully 99%+ of the time

---

## 5. Non-Functional Requirements

### 5.1 Performance (NFR-P)

**NFR-P-001: Response Time**
- Data fetching MUST complete within 30 seconds per source
- Total report generation MUST complete within 60 seconds
- Claude API calls SHOULD complete within 45 seconds
- File saving operations MUST complete within 5 seconds

**NFR-P-002: Resource Usage**
- System MUST use less than 100 MB memory during execution
- System MUST use less than 10 MB disk space (excluding reports)
- Log files MUST not exceed 10 MB before rotation
- CPU usage SHOULD be minimal between scheduled runs

**NFR-P-003: Scalability**
- System MUST handle addition of new data sources without performance degradation
- System MUST support up to 10 simultaneous data sources
- System MUST handle reports up to 20 KB without issues

### 5.2 Reliability (NFR-R)

**NFR-R-001: Availability**
- System MUST achieve 99% successful report generation rate
- System MUST recover automatically from transient network errors
- System MUST continue operation if individual data sources fail
- System MUST not crash due to malformed data

**NFR-R-002: Data Integrity**
- System MUST not corrupt existing reports when saving new ones
- System MUST validate all output is well-formed before saving
- System MUST preserve data accuracy from sources
- System MUST maintain referential integrity in links

**NFR-R-003: Error Recovery**
- System MUST log all errors with sufficient detail for debugging
- System MUST attempt fallback strategies before failing
- System MUST continue partial execution even with failures
- System SHOULD notify user of persistent failures

### 5.3 Usability (NFR-U)

**NFR-U-001: Installation**
- Installation MUST complete with single setup script execution
- Setup MUST validate all dependencies are installable
- Setup MUST provide clear success/failure messages
- Installation SHOULD complete within 5 minutes on typical system

**NFR-U-002: Configuration**
- Configuration MUST use human-readable YAML format
- Configuration MUST include comments explaining all options
- Configuration MUST validate on load with helpful error messages
- Default configuration MUST work for typical use case

**NFR-U-003: Documentation**
- System MUST include README with quick start instructions
- System MUST include comprehensive architecture documentation (CLAUDE.md)
- System MUST include examples for all configuration options
- Documentation MUST be up-to-date with code

**NFR-U-004: Monitoring**
- Logs MUST be human-readable
- Logs MUST include timestamps for all events
- Logs MUST distinguish between INFO, WARNING, and ERROR levels
- Status MUST be checkable with simple command

### 5.4 Maintainability (NFR-M)

**NFR-M-001: Code Quality**
- Code MUST follow PEP 8 style guidelines
- Code MUST include docstrings for all classes and public methods
- Code MUST use meaningful variable and function names
- Code SHOULD include type hints where beneficial

**NFR-M-002: Modularity**
- System MUST separate concerns into distinct modules
- Components MUST have clear, well-defined interfaces
- Changes to one module SHOULD NOT require changes to unrelated modules
- New features SHOULD be addable without modifying core logic

**NFR-M-003: Testing**
- Code MUST be testable (currently manual testing)
- Critical functions SHOULD have test coverage
- Regression testing SHOULD be performed before releases
- Setup script MUST include test run verification

**NFR-M-004: Versioning**
- Code SHOULD be version controlled (git)
- Major changes SHOULD be documented in version history
- Breaking changes MUST be clearly documented
- Backward compatibility SHOULD be maintained where possible

### 5.5 Security (NFR-S)

**NFR-S-001: Credential Management**
- API keys MUST be stored in .env file
- .env file MUST be excluded from version control
- API keys MUST NOT appear in logs
- System MUST provide .env.example template

**NFR-S-002: Data Privacy**
- System MUST NOT collect personal user data
- System MUST NOT transmit data except to configured services
- API calls MUST use HTTPS
- Logs MUST NOT contain sensitive information

**NFR-S-003: Input Validation**
- System MUST validate all configuration inputs
- System MUST sanitize data from external sources
- System MUST prevent code injection via configuration
- System MUST handle malicious data safely

### 5.6 Compatibility (NFR-C)

**NFR-C-001: Platform Support**
- System MUST run on macOS (primary platform)
- System SHOULD run on Linux
- System MAY run on Windows with minor adjustments
- System MUST work on Python 3.7+

**NFR-C-002: Obsidian Integration**
- Markdown output MUST be compatible with Obsidian
- Files MUST be detectable by Obsidian's file watcher
- Links MUST work within Obsidian
- Metadata MUST be Obsidian-compatible

**NFR-C-003: Browser Compatibility**
- HTML output MUST render in all modern browsers
- HTML MUST be valid HTML5
- Links MUST open correctly in browsers
- No JavaScript dependencies for viewing

---

## 6. System Architecture

### 6.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                     │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │
│  │   HTML     │  │  Markdown  │  │  JSON / Text    │  │
│  │  Reports   │  │  Reports   │  │    Reports      │  │
│  └────────────┘  └────────────┘  └─────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  APPLICATION LAYER                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Space Weather Automation Engine                 │  │
│  │  - Configuration Management                      │  │
│  │  - Data Collection Orchestration                 │  │
│  │  - Report Generation Coordination                │  │
│  │  - File Management                               │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Enhanced Claude Integration                     │  │
│  │  - Prompt Engineering                            │  │
│  │  - API Communication                             │  │
│  │  - Format Conversion                             │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   DATA ACCESS LAYER                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   HTTP      │  │   Browser    │  │  File I/O    │  │
│  │   Client    │  │     MCP      │  │   Handler    │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  EXTERNAL SERVICES                       │
│  ┌─────────┐  ┌────────┐  ┌──────────┐  ┌──────────┐  │
│  │  NOAA   │  │UK Met  │  │ Claude   │  │  Other   │  │
│  │  SWPC   │  │ Office │  │   API    │  │ Sources  │  │
│  └─────────┘  └────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Component Breakdown

**Core Components:**

1. **space_weather_automation.py** (371 lines)
   - Main orchestrator
   - Configuration loading
   - Data collection pipeline
   - Report generation coordination
   - File management
   - Cleanup operations

2. **claude_integration_enhanced.py** (402 lines)
   - Claude API integration
   - Prompt engineering (200+ lines)
   - Format conversion (HTML/MD/JSON/TXT)
   - Fallback report generation
   - Error handling

3. **scheduler.py** (73 lines)
   - Foreground scheduling
   - Interval-based execution
   - Progress indicators

4. **setup.sh** (128 lines)
   - Dependency installation
   - launchd configuration
   - Service activation

**Support Components:**

5. **config.yaml**
   - Data source URLs
   - Output format configuration
   - Schedule settings
   - Logging configuration

6. **.env**
   - API keys (Anthropic)
   - Secrets management

**Alternative Implementations (code/ directory):**
- enhanced_automation.py - Browser fallback detection
- browser_mcp_workflow.py - MCP request/response workflow
- browser_mcp_fetcher.py - Browser automation utilities
- browser_scraping.py - Alternative scraping methods

### 6.3 Data Flow

```
1. TRIGGER (launchd/scheduler/manual)
   ↓
2. LOAD CONFIGURATION (config.yaml, .env)
   ↓
3. INITIALIZE LOGGING
   ↓
4. FETCH DATA (parallel where possible)
   ├─ NOAA SWPC Discussion
   ├─ UK Met Office Forecast
   ├─ SpaceWeather.com
   ├─ EarthSky.org
   └─ SpaceWeatherLive.com
   ↓
5. VALIDATE DATA
   ↓
6. GENERATE REPORT (Claude API)
   ├─ Build comprehensive prompt
   ├─ Call Anthropic API
   ├─ Parse response
   └─ Fallback to templates if needed
   ↓
7. CONVERT FORMATS
   ├─ Extract HTML
   ├─ Convert to Markdown
   ├─ Generate JSON
   └─ Convert to Text
   ↓
8. SAVE FILES
   ├─ space_weather_YYYY-MM-DD_HHMM.html
   ├─ space_weather_YYYY-MM-DD_HHMM.md
   ├─ space_weather_YYYY-MM-DD_HHMM.json
   └─ space_weather_YYYY-MM-DD_HHMM.txt
   ↓
9. CLEANUP OLD REPORTS (>30 days)
   ↓
10. LOG COMPLETION
```

### 6.4 Deployment Architecture

**Development Environment:**
- Local macOS development
- Manual execution for testing
- Direct log viewing

**Production Environment:**
- macOS with launchd service
- Background execution every 6 hours
- Automatic log rotation
- Obsidian vault integration

**Future: Cloud Deployment (Potential)**
- Docker container
- Kubernetes cron job
- Centralized logging
- Multi-user support

---

## 7. Data Sources

### 7.1 Primary Sources

**NOAA SWPC (Space Weather Prediction Center)**
- **URL:** `https://services.swpc.noaa.gov/text/discussion.txt`
- **Priority:** PRIMARY (highest)
- **Content Type:** Plain text discussion
- **Update Frequency:** Multiple times daily (typically every 3-6 hours)
- **Reliability:** Very High (99.9%+ uptime)
- **Authority:** Official US government source
- **Typical Size:** 5-10 KB
- **Format:** Structured text with sections
- **Coverage:**
  - Solar activity summary
  - Active region analysis
  - Flare forecasts
  - Geomagnetic forecasts
  - CME analysis

**UK Met Office Space Weather**
- **URL:** `https://weather.metoffice.gov.uk/specialist-forecasts/space-weather`
- **Priority:** PRIMARY
- **Content Type:** HTML page
- **Update Frequency:** Daily
- **Reliability:** High (99%+ uptime)
- **Authority:** Official UK meteorological service
- **Typical Size:** Variable (HTML page)
- **Format:** HTML with structured sections
- **Coverage:**
  - Solar activity overview
  - Geomagnetic conditions
  - 3-day forecast
  - Aurora predictions

### 7.2 Alternative/Supplementary Sources

**SpaceWeather.com**
- **URL:** `https://www.spaceweather.com/`
- **Priority:** ALTERNATIVE
- **Content Type:** HTML page
- **Update Frequency:** Daily
- **Reliability:** High
- **Authority:** Popular enthusiast site (Dr. Tony Phillips)
- **Coverage:**
  - Current solar activity
  - Sunspot images
  - Aurora alerts
  - Educational content

**EarthSky.org Sun News**
- **URL:** `https://earthsky.org/sun/sun-news-activity-solar-flare-cme-aurora-updates/`
- **Priority:** ALTERNATIVE
- **Content Type:** HTML news page
- **Update Frequency:** Daily to weekly
- **Reliability:** Medium-High
- **Authority:** Science communication organization
- **Coverage:**
  - Solar news articles
  - Educational explanations
  - Aurora updates

**SpaceWeatherLive.com**
- **URL:** `https://www.spaceweatherlive.com/en/solar-activity.html`
- **Priority:** ALTERNATIVE
- **Content Type:** HTML page with live data
- **Update Frequency:** Real-time
- **Reliability:** High
- **Authority:** Community-run real-time monitoring
- **Coverage:**
  - Live solar wind data
  - Flare lists
  - Geomagnetic indices
  - Historical data

### 7.3 Future/Optional Sources

**LMSAL Solar Flares (robots.txt restricted)**
- **URL:** `https://www.lmsal.com/solarsoft/last_events/`
- **Priority:** OPTIONAL (requires Browser MCP)
- **Content Type:** HTML table
- **Status:** Infrastructure ready, not currently active
- **Coverage:**
  - Comprehensive flare list
  - Precise timing
  - Active region attribution

### 7.4 Source Selection Strategy

**Prioritization Logic:**
1. Always attempt primary sources first (NOAA, UK Met Office)
2. Use alternative sources for additional context
3. Continue report generation with available data if some sources fail
4. Log all fetch attempts with success/failure status
5. Fallback to browser automation if HTTP blocked (future capability)

**Quality Indicators:**
- Content length >100 bytes
- No error page indicators
- Reasonable response time (<30 seconds)
- Expected structure present

---

## 8. AI Integration

### 8.1 Claude API Configuration

**Model Selection:**
- **Model:** `claude-sonnet-4-20250514`
- **Rationale:** Balance of quality, speed, and cost
- **Capabilities:**
  - Extended context window (200K tokens)
  - High-quality natural language generation
  - Instruction following
  - Professional writing style

**API Parameters:**
- **Max Tokens:** 16,000 (sufficient for detailed reports)
- **Temperature:** 0.7 (slightly creative for natural writing)
- **Top P:** Default
- **Messages Format:** Single user message with comprehensive prompt

**Performance Characteristics:**
- **Average Response Time:** ~30 seconds
- **Token Usage:** ~6,000 tokens per report
  - Input: ~2,000 tokens (data + prompt)
  - Output: ~4,000 tokens (formatted report)
- **Success Rate:** 100% (recent production runs)
- **Cost per Report:** ~$0.10 (estimated)

### 8.2 Prompt Engineering

**Prompt Structure (200+ lines):**

1. **System Context**
   - Role definition: "Expert space weather forecaster"
   - Task description: "Create comprehensive daily report"
   - Target date and coverage period (UTC)

2. **Primary Data Sources**
   - NOAA SWPC Discussion (full text)
   - UK Met Office forecast (extracted content)
   - Labeled as "Most Authoritative"

3. **Supplementary Sources**
   - Alternative sources for context
   - Clearly separated from primary sources
   - Noted as supporting information

4. **Report Structure Requirements**
   - Header section template
   - Top story paragraph guidelines
   - Detailed section requirements:
     - Flare activity (with specific UTC times)
     - Sunspot regions (AR numbers, classifications)
     - CME activity (geoeffectiveness)
     - Solar wind parameters (speed, IMF Bz)
     - Geomagnetic conditions (Kp, G-scale)
     - Forecast section (3-day outlook)

5. **Critical Detail Requirements**
   - Always include exact UTC times with links
   - Specify active region numbers (AR####)
   - Provide magnetic classifications with links
   - Use proper flare terminology (C/M/X class)
   - Include NOAA scale ratings (R1-R5, G1-G5)
   - Mention radio blackout impacts
   - List specific probability percentages

6. **Linking Requirements (15+ types)**
   - UTC times → Universal Time explanation
   - NOAA scales → Official scale documentation
   - Radio blackouts → Phenomenon explanation
   - Solar flare classes → Wikipedia/educational resources
   - X-class flares → EarthSky detailed articles
   - CMEs → What are CMEs
   - Magnetic classifications → SpaceWeatherLive reference
   - IMF → Interplanetary Magnetic Field explanation
   - Bz component → Bz level explanation
   - Kp index → Planetary K-index documentation

7. **Writing Style Guide**
   - Tone: Professional yet accessible
   - Voice: Active voice primarily
   - Technical precision: Use exact values from data
   - Natural flow: Coherent narrative, not just bullets
   - Context: Solar cycle context, seasonal effects

8. **Quality Checklist**
   - All times in UTC and properly linked
   - All active region numbers included
   - Magnetic classifications provided
   - Flare classes and exact times listed
   - CME geoeffectiveness assessed
   - Solar wind parameters included
   - Forecast probabilities specified
   - All links functional and appropriate

### 8.3 Fallback Strategy

**When Claude API Unavailable:**
1. Log the API failure with error details
2. Switch to basic template generation
3. Use simple formatting with fetched data
4. Mark report as "Basic Template (Claude API unavailable)"
5. Include all fetched data in structured format
6. Save in all requested formats

**Fallback Template Features:**
- Includes all source data verbatim
- Basic HTML structure
- Timestamped header
- Source attribution
- No AI-generated narrative
- Still useful for information access

### 8.4 Cost Analysis

**Current Usage:**
- Runs: 4 per day (6-hour intervals)
- Tokens per run: ~6,000
- Daily tokens: ~24,000
- Monthly tokens: ~720,000
- Annual tokens: ~8.6 million

**Estimated Costs (based on Claude Sonnet pricing):**
- Daily: ~$0.40
- Monthly: ~$6-8
- Annual: ~$75-95

**Cost Optimization Opportunities:**
- Cache common prompt sections (not yet implemented)
- Use smaller model for simple days (not yet implemented)
- Reduce token usage via prompt optimization (ongoing)

---

## 9. Output Formats

### 9.1 HTML Format

**Specification:**
- **Standard:** HTML5
- **Semantic Tags:** h3, h4, p, ul, li, strong, a
- **Link Attributes:**
  - `target="_blank"` for external links
  - `rel="noopener"` for security
- **No CSS:** Plain HTML, readable without styling
- **Typical Size:** 1-8 KB

**Structure:**
```html
<h3>Sun news November 02 (UTC): [Headline]</h3>
<h4>(11 UTC November 01 → 11 UTC November 02)</h4>

<p>[Opening narrative paragraph]</p>

<ul>
  <li><strong>Flare activity:</strong> [Details]
    <ul>
      <li><strong>Strongest flare:</strong> [Details with linked time]</li>
      <li>Other notable flares: [List]</li>
    </ul>
  </li>
  <li><strong>Sunspot regions:</strong> [Details]
    <ul>
      <li><strong>AR####</strong> [Location, classification, activity]</li>
    </ul>
  </li>
  <li><strong>CME activity:</strong> [Details]</li>
  <li><strong>Solar wind:</strong> [Parameters]</li>
  <li><strong>Earth's magnetic field:</strong> [Conditions]</li>
</ul>

<h3>What's ahead? Sun–Earth forecast</h3>
<ul>
  <li><strong>Flare activity forecast:</strong> [Predictions]</li>
  <li><strong>Geomagnetic activity forecast:</strong>
    <ul>
      <li><strong>[Date]:</strong> [Forecast]</li>
      <li><strong>[Date+1]:</strong> [Forecast]</li>
      <li><strong>[Date+2]:</strong> [Forecast]</li>
    </ul>
  </li>
</ul>
```

**Use Cases:**
- Direct browser viewing
- Email distribution
- Archival viewing
- Copying to other documents

### 9.2 Markdown Format

**Specification:**
- **Variant:** GitHub-Flavored Markdown
- **Compatibility:** Obsidian-compatible
- **Conversion:** HTML → Markdown via automated process
- **Typical Size:** 1-5 KB

**Structure:**
```markdown
## Sun news November 02 (UTC): [Headline]
### (11 UTC November 01 → 11 UTC November 02)

[Opening narrative paragraph]

- **Flare activity:** [Details]
  - **Strongest flare:** [Details with linked time]
  - Other notable flares: [List]

- **Sunspot regions:** [Details]
  - **AR####** [Location, classification, activity]

- **CME activity:** [Details]
- **Solar wind:** [Parameters]
- **Earth's magnetic field:** [Conditions]

## What's ahead? Sun–Earth forecast

- **Flare activity forecast:** [Predictions]
- **Geomagnetic activity forecast:**
  - **[Date]:** [Forecast]
  - **[Date+1]:** [Forecast]
  - **[Date+2]:** [Forecast]
```

**Obsidian Features:**
- Can be embedded in daily notes: `![[space_weather_2025-11-02_1643]]`
- Searchable across vault
- Links preserved as Markdown links
- Can add tags and frontmatter
- Appears in graph view if linked

**Use Cases:**
- Obsidian vault integration
- Git-based documentation
- Plain text archival
- Easy editing and annotation

### 9.3 JSON Format

**Specification:**
- **Standard:** Valid JSON (RFC 8259)
- **Pretty Printed:** 2-space indentation
- **Typical Size:** ~470 KB (includes full source data)

**Structure:**
```json
{
  "timestamp": "2025-11-02T16:43:00.000000+00:00",
  "date_range": {
    "start": "2025-11-01 11:00 UTC",
    "end": "2025-11-02 11:00 UTC"
  },
  "sources": {
    "noaa_discussion": "[Full text of NOAA discussion]",
    "uk_met_office": "[Extracted content]",
    "spaceweather_com": "[Content snippet]",
    "earthsky": "[Content snippet]",
    "spaceweatherlive": "[Content snippet]"
  },
  "report_html": "[Full HTML report]",
  "generated_with": "enhanced_claude",
  "model": "claude-sonnet-4-20250514",
  "generation_time": "2025-11-02T16:43:18.000000+00:00"
}
```

**Use Cases:**
- Data analysis and research
- Programmatic access to report data
- Machine learning training data
- API integration
- Archival with full context

### 9.4 Plain Text Format

**Specification:**
- **Encoding:** UTF-8
- **Line Endings:** Unix (LF)
- **Format:** HTML tags stripped, structure preserved
- **Typical Size:** 1-3 KB

**Structure:**
```
Sun news November 02 (UTC): [Headline]
(11 UTC November 01 → 11 UTC November 02)

[Opening narrative paragraph]

Flare activity: [Details]
  Strongest flare: [Details]
  Other notable flares: [List]

Sunspot regions: [Details]
  AR#### [Location, classification, activity]

CME activity: [Details]
Solar wind: [Parameters]
Earth's magnetic field: [Conditions]

What's ahead? Sun–Earth forecast

Flare activity forecast: [Predictions]
Geomagnetic activity forecast:
  [Date]: [Forecast]
  [Date+1]: [Forecast]
  [Date+2]: [Forecast]
```

**Use Cases:**
- Terminal viewing (cat, less, more)
- Email (plain text)
- Screen readers
- Minimal storage requirements
- Universal compatibility

### 9.5 Format Configuration

**config.yaml:**
```yaml
output:
  formats:
    html: true        # Enable HTML output
    markdown: true    # Enable Markdown output
    json: true        # Enable JSON output
    text: true        # Enable plain text output
    pdf: false        # PDF not yet implemented
```

**Flexibility:**
- Enable/disable any format independently
- All formats generated in single run
- Same base filename with different extensions
- Configurable output directory

---

## 10. Automation & Scheduling

### 10.1 launchd Service (macOS)

**Service Configuration:**
- **Label:** `com.user.spaceweather`
- **Plist Location:** `~/Library/LaunchAgents/com.user.spaceweather.plist`
- **Interval:** 21600 seconds (6 hours)
- **RunAtLoad:** true (executes immediately at login)
- **KeepAlive:** false (runs on interval, not continuously)

**Plist Structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.spaceweather</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>[path]/space_weather_automation.py</string>
    </array>

    <key>StartInterval</key>
    <integer>21600</integer>

    <key>RunAtLoad</key>
    <true/>

    <key>WorkingDirectory</key>
    <string>[project-directory]</string>

    <key>StandardOutPath</key>
    <string>[project-directory]/stdout.log</string>

    <key>StandardErrorPath</key>
    <string>[project-directory]/stderr.log</string>
</dict>
</plist>
```

**Setup Process:**
1. Run `./setup.sh`
2. Script installs dependencies
3. Script creates plist file
4. Script loads service with launchctl
5. Service starts immediately
6. Service runs every 6 hours automatically

**Management Commands:**
```bash
# Load service (start)
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist

# Unload service (stop)
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist

# Check if running
launchctl list | grep spaceweather

# View logs
tail -f space_weather_automation.log
tail -f stdout.log
tail -f stderr.log
```

**Current Status:**
- ✓ Service likely active (based on log evidence)
- ✓ Regular 6-hour execution pattern observed
- ✓ Last runs: 10:43 and 16:43 (6-hour gap)
- ✓ All runs successful

### 10.2 Python Scheduler (Alternative)

**File:** scheduler.py (73 lines)

**Features:**
- Foreground execution (runs in terminal)
- Visual progress indicators
- Immediate execution on startup
- Configurable interval or specific times
- Graceful Ctrl+C shutdown

**Configuration (config.yaml):**
```yaml
schedule:
  interval_hours: 6              # Run every 6 hours
  specific_times: []             # Alternative: ["00:00", "06:00", "12:00", "18:00"]
```

**Usage:**
```bash
# Start scheduler (foreground)
python3 scheduler.py

# Output:
# Starting Space Weather Report Scheduler...
# Configuration: Every 6 hours
# Running initial report generation...
# [Report generation output]
# Next run scheduled in 6 hours
# Press Ctrl+C to stop
#
# Sleeping... (checks every 60 seconds)
```

**When to Use:**
- Development and testing
- Want to see real-time output
- Don't want background service
- Temporary automation needs
- Debugging scheduling issues

### 10.3 Manual Execution

**On-Demand Report Generation:**
```bash
python3 space_weather_automation.py
```

**Use Cases:**
- Immediate report needed
- Testing after configuration changes
- Debugging data source issues
- Verifying setup
- Ad-hoc information requests

**Expected Behavior:**
- Runs once and exits
- Outputs to console and log file
- Generates all enabled formats
- Returns exit code 0 on success

### 10.4 Execution Timeline

**Typical 6-Hour Cycle:**
```
00:00 - Previous run completes
      - System idle (launchd service waiting)

06:00 - launchd triggers execution
00:01 - Python interpreter starts
00:02 - Configuration loaded
00:03 - Logging initialized
00:05 - Data fetching begins (5 sources in parallel)
00:10 - Data fetching completes (~5 seconds actual)
00:11 - Claude prompt constructed
00:12 - Claude API called
00:42 - Claude response received (~30 seconds)
00:43 - Format conversion (HTML→MD, JSON, TXT)
00:45 - Files saved (4 formats)
00:46 - Old reports cleaned up
00:47 - Execution completes
00:48 - Process exits
      - System idle until next trigger

12:00 - Next automatic execution
```

**Total Active Time:** ~40-50 seconds per run
**Idle Time:** ~5 hours 59 minutes between runs

---

## 11. Configuration Management

### 11.1 config.yaml Structure

**Complete Configuration:**
```yaml
# Primary authoritative data sources
primary_sources:
  noaa_discussion: "https://services.swpc.noaa.gov/text/discussion.txt"
  uk_met_office: "https://weather.metoffice.gov.uk/specialist-forecasts/space-weather"

# Alternative/supplementary sources
alternative_sources:
  spaceweather_com: "https://www.spaceweather.com/"
  earthsky: "https://earthsky.org/sun/sun-news-activity-solar-flare-cme-aurora-updates/"
  spaceweatherlive: "https://www.spaceweatherlive.com/en/solar-activity.html"

# Flare-specific sources (optional, may be blocked)
flare_sources:
  primary: "https://www.lmsal.com/solarsoft/last_events/"
  fallback_search: "solar flares today NOAA"
  fallback_site: "https://www.spaceweather.com/"

# Output configuration
output:
  base_directory: "/Users/cayoung/Documents/Obsidian/CAY-power-vault/space-weather-reports/reports"
  formats:
    html: true
    markdown: true
    json: true
    text: true
    pdf: false
  filename_pattern: "space_weather_{date}_{time}"
  archive: true
  max_archive_days: 30

# Report configuration
report:
  timezone: "UTC"
  date_format: "%Y-%m-%d"
  time_format: "%H%M"

# Scheduling configuration
schedule:
  interval_hours: 6
  specific_times: []

# Logging configuration
logging:
  level: "INFO"
  file: "space_weather_automation.log"
  max_size_mb: 10
  backup_count: 5
  format: "%(asctime)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```

### 11.2 .env File (Secrets)

**Structure:**
```bash
# Anthropic Claude API Key
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Optional: Email notifications (future)
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# NOTIFICATION_EMAIL=recipient@example.com

# Optional: Browser MCP configuration (future)
# CHROME_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
# MCP_TIMEOUT=30
```

**Security:**
- File MUST be in .gitignore
- Permissions SHOULD be 600 (owner read/write only)
- Never committed to version control
- Template provided as .env.example

### 11.3 Configuration Loading

**Process:**
1. Load config.yaml with PyYAML
2. Validate all required sections present
3. Load .env with python-dotenv
4. Merge configurations
5. Apply defaults for missing optional values
6. Validate configuration integrity
7. Log configuration summary (without secrets)

**Validation Rules:**
- At least one primary source required
- Output directory must be writable
- At least one output format enabled
- Schedule interval >0 or specific times provided
- Log file path must be writable
- Timezone must be valid

**Error Handling:**
- Missing config.yaml → Fail with clear message
- Missing .env → Warning, proceed without API key (use templates)
- Invalid YAML syntax → Fail with parse error
- Invalid paths → Fail before execution
- Missing sections → Use defaults where possible

---

## 12. Error Handling & Resilience

### 12.1 Data Fetching Errors

**HTTP Request Failures:**
```python
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    logger.info(f"Successfully fetched {source_name}")
    return response.text
except requests.exceptions.Timeout:
    logger.error(f"Timeout fetching {source_name} after 30 seconds")
    return None
except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP error {e.response.status_code} for {source_name}")
    if e.response.status_code == 403:
        logger.info(f"Robots.txt block detected for {source_name}")
        # Future: Trigger browser automation
    return None
except requests.exceptions.RequestException as e:
    logger.error(f"Request failed for {source_name}: {e}")
    return None
```

**Resilience Strategy:**
- Continue execution if individual sources fail
- Log all failures with details
- Proceed with available data
- Report generation uses whatever data was successfully fetched
- Minimum viable data: NOAA discussion alone is sufficient

**Failure Scenarios:**
- **All sources fail:** Generate minimal template report
- **Primary sources fail:** Use alternative sources
- **Network down:** Log error, retry on next scheduled run
- **Source structure changed:** May result in empty sections, but no crash

### 12.2 Claude API Errors

**API Call Failures:**
```python
try:
    from claude_integration_enhanced import EnhancedClaudeReportGenerator
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        logger.warning("No API key found, using basic templates")
        return self.generate_basic_templates(data)

    logger.info("Using enhanced Claude report generation")
    generator = EnhancedClaudeReportGenerator(api_key)
    reports = generator.generate_report(data)
    logger.info("Successfully generated report with enhanced Claude")
    return reports

except Exception as e:
    logger.error(f"Claude integration failed: {e}", exc_info=True)
    logger.info("Falling back to basic templates")
    return self.generate_basic_templates(data)
```

**Resilience Strategy:**
- Always have fallback templates ready
- Graceful degradation to basic reports
- Log API errors with full stack trace
- Continue execution, don't fail entire run
- User still gets report, just simpler format

**Failure Scenarios:**
- **No API key:** Use templates (expected for initial setup)
- **API rate limit:** Log error, use template, retry next run
- **API timeout:** Fall back to templates after 60 seconds
- **Invalid response:** Log error, parse what's possible, use templates if needed
- **Network error:** Fall back to templates

### 12.3 File I/O Errors

**File Writing Failures:**
```python
try:
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"Saved report: {filepath}")
except PermissionError:
    logger.error(f"Permission denied writing {filepath}")
except OSError as e:
    logger.error(f"OS error writing {filepath}: {e}")
except Exception as e:
    logger.error(f"Unexpected error writing {filepath}: {e}")
```

**Resilience Strategy:**
- Try each format independently
- One format failure doesn't stop others
- Log specific error for each failure
- Continue with remaining formats
- At least partial output better than none

**Failure Scenarios:**
- **Disk full:** Log error, save what fits, warn user
- **Permission denied:** Log error with path, continue other formats
- **Directory missing:** Attempt to create, log if fails
- **Filename conflict:** Timestamp should prevent, but log if occurs

### 12.4 Configuration Errors

**Config Loading Failures:**
```python
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    logger.info("Configuration loaded successfully")
    return config
except FileNotFoundError:
    logger.error("config.yaml not found in current directory")
    sys.exit(1)
except yaml.YAMLError as e:
    logger.error(f"Invalid YAML syntax in config.yaml: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error loading configuration: {e}")
    sys.exit(1)
```

**Resilience Strategy:**
- Fail fast on configuration errors (can't run without config)
- Provide clear, actionable error messages
- Point user to documentation
- Exit cleanly with appropriate exit code

### 12.5 Logging Errors

**Log File Issues:**
```python
try:
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_size_mb * 1024 * 1024,
        backupCount=backup_count
    )
    logger.addHandler(handler)
except PermissionError:
    print(f"Warning: Cannot write to {log_file}, logging to console only")
    # Continue with console logging only
except Exception as e:
    print(f"Warning: Logging setup failed: {e}")
    # Continue with basic console logging
```

**Resilience Strategy:**
- Logging failure doesn't stop execution
- Fall back to console-only logging
- Warn user but continue operation
- At least some logging better than none

---

## 13. Logging & Monitoring

### 13.1 Log File Configuration

**Primary Log:** space_weather_automation.log

**Configuration:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            'space_weather_automation.log',
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        ),
        logging.StreamHandler()  # Also log to console
    ]
)
```

**Rotation Policy:**
- Maximum size: 10 MB per file
- Backup count: 5 files
- Total maximum: 60 MB (6 files × 10 MB)
- Oldest backup deleted when limit reached
- Automatic rotation when size exceeded

**Log Levels:**
- **INFO:** Normal operations (fetches, generation, saves)
- **WARNING:** Non-critical issues (missing optional data, fallbacks)
- **ERROR:** Failures that don't stop execution (source fetch fails)
- **CRITICAL:** Not currently used (would be for total failures)

### 13.2 Log Entry Types

**Initialization:**
```
2025-11-02 16:43:18 - INFO - Space Weather Report Generator initialized
2025-11-02 16:43:18 - INFO - Starting report generation...
```

**Data Fetching:**
```
2025-11-02 16:43:19 - INFO - Successfully fetched NOAA discussion
2025-11-02 16:43:20 - INFO - Successfully fetched UK Met Office data
2025-11-02 16:43:21 - INFO - Successfully fetched spaceweather_com
2025-11-02 16:43:21 - INFO - Successfully fetched earthsky
2025-11-02 16:43:22 - INFO - Successfully fetched spaceweatherlive
```

**Report Generation:**
```
2025-11-02 16:43:22 - INFO - Generating report with Claude...
2025-11-02 16:43:22 - INFO - Using enhanced Claude report generation
2025-11-02 16:43:52 - INFO - Successfully generated report with enhanced Claude
```

**File Operations:**
```
2025-11-02 16:43:53 - INFO - Saved report: /path/to/reports/space_weather_2025-11-02_1643.html
2025-11-02 16:43:53 - INFO - Saved report: /path/to/reports/space_weather_2025-11-02_1643.md
2025-11-02 16:43:53 - INFO - Saved report: /path/to/reports/space_weather_2025-11-02_1643.json
2025-11-02 16:43:53 - INFO - Saved report: /path/to/reports/space_weather_2025-11-02_1643.txt
```

**Completion:**
```
2025-11-02 16:43:54 - INFO - Successfully generated 4 report(s)
```

**Errors (Example):**
```
2025-11-02 16:43:20 - ERROR - Failed to fetch spaceweather_com: Timeout after 30 seconds
2025-11-02 16:43:22 - WARNING - No API key found, using basic templates
2025-11-02 16:43:25 - ERROR - Claude integration failed: API rate limit exceeded
2025-11-02 16:43:25 - INFO - Falling back to basic templates
```

### 13.3 Additional Log Files

**stdout.log (launchd)**
- Standard output from launchd execution
- Typically empty (all output goes to main log)
- Size: 0 bytes (current)

**stderr.log (launchd)**
- Error output from launchd execution
- May contain Python warnings/errors
- Size: 5 KB (current)
- Contains urllib3 SSL warnings (non-critical)

**test_run.log**
- Output from setup.sh test execution
- Used for verifying installation
- Size: 1.6 KB (current)

### 13.4 Monitoring Strategies

**Health Check Commands:**
```bash
# Check if service is running
launchctl list | grep spaceweather

# View recent log entries
tail -n 50 space_weather_automation.log

# Follow log in real-time
tail -f space_weather_automation.log

# Check for errors in last hour
grep ERROR space_weather_automation.log | tail -n 20

# Check last successful run
grep "Successfully generated" space_weather_automation.log | tail -n 1

# Count successful runs today
grep "$(date +%Y-%m-%d)" space_weather_automation.log | grep "Successfully generated" | wc -l

# Check for API usage
grep "enhanced Claude" space_weather_automation.log | tail -n 10
```

**Expected Patterns:**
- 4 successful runs per day (every 6 hours)
- Each run takes ~30-50 seconds
- All 5 data sources fetched successfully
- Enhanced Claude generation used
- All 4 formats saved
- No ERROR or WARNING messages (ideal state)

**Alert Indicators:**
- Multiple ERROR messages in succession
- No successful runs for >6 hours
- All data sources failing
- Persistent Claude API failures
- Disk space warnings
- Permission errors

### 13.5 Performance Metrics

**Tracked Metrics:**
- Data fetch duration (per source)
- Claude API response time
- Total execution time
- File save operations
- Success/failure rates

**Current Performance (from logs):**
- Data fetching: 3-5 seconds total (all sources)
- Claude API: ~30 seconds
- Format conversion: <1 second
- File saving: <1 second
- Total: ~40 seconds per run
- Success rate: 100% (recent runs)

---

## 14. Security & Privacy

### 14.1 Credential Management

**API Key Storage:**
- Stored in `.env` file (not in code)
- `.env` excluded from version control via `.gitignore`
- File permissions SHOULD be 600 (owner read/write only)
- Template provided as `.env.example` (no actual key)

**Loading Process:**
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file
api_key = os.getenv('ANTHROPIC_API_KEY')

if not api_key:
    logger.warning("No API key found, using basic templates")
    # Continue without API (degraded functionality)
```

**Key Protection:**
- Never logged (even at DEBUG level)
- Never included in error messages
- Never committed to git
- Never transmitted except to Anthropic API
- Only loaded when needed

### 14.2 Data Privacy

**Personal Data Collection:**
- System does NOT collect personal user data
- No usage analytics transmitted
- No user behavior tracking
- All data processing local

**Data Transmission:**
- External requests only to configured data sources
- Claude API calls include only space weather data (public information)
- No user-identifying information in API calls
- All transmissions over HTTPS

**Data Storage:**
- All reports stored locally
- No cloud storage without explicit user configuration
- User controls all data retention
- Reports can be deleted anytime

### 14.3 Network Security

**HTTPS Requirements:**
- All external requests use HTTPS
- Certificate validation enabled (not disabled)
- No insecure HTTP fallback
- Timeout protection (30 seconds max)

**API Security:**
- Anthropic API uses HTTPS
- API key sent in Authorization header (not URL)
- Modern TLS version required
- No certificate pinning (relies on system trust store)

### 14.4 Input Validation

**Configuration Validation:**
```python
# Validate URLs
parsed = urllib.parse.urlparse(url)
if parsed.scheme not in ['http', 'https']:
    raise ValueError("Invalid URL scheme")

# Validate paths
base_dir = os.path.abspath(base_directory)
if not os.path.exists(base_dir):
    os.makedirs(base_dir)  # Create if missing
if not os.access(base_dir, os.W_OK):
    raise PermissionError("Directory not writable")

# Validate retention days
max_days = int(max_archive_days)
if max_days < 1:
    raise ValueError("Retention must be at least 1 day")
```

**Data Source Content:**
- Fetched data treated as untrusted
- No code execution from fetched content
- HTML entities escaped where appropriate
- No eval() or exec() of external data

### 14.5 File System Security

**Path Traversal Protection:**
```python
# Ensure filename doesn't escape directory
filename = os.path.basename(filename)  # Strip any path components
filepath = os.path.join(base_dir, filename)
filepath = os.path.abspath(filepath)

# Verify still within base directory
if not filepath.startswith(os.path.abspath(base_dir)):
    raise ValueError("Path traversal attempt detected")
```

**File Permissions:**
- Generated files: 644 (owner read/write, others read)
- Configuration files: 644 (readable for ease of use)
- .env file: SHOULD be 600 (owner only)
- Log files: 644 (readable for monitoring)

### 14.6 Dependency Security

**Known Vulnerabilities:**
- Regular dependency updates recommended
- urllib3 warning about OpenSSL (non-critical, logged)
- No known critical vulnerabilities in current dependencies

**Update Strategy:**
- Pin major versions in requirements.txt
- Allow minor/patch updates (>=)
- Test after updates
- Review security advisories periodically

**Supply Chain:**
- Dependencies from PyPI (official Python package index)
- No custom/private package sources
- Requirements.txt locks major versions
- Anthropic SDK from official source

---

## 15. Future Enhancements

### 15.1 Near-Term (Ready to Implement)

**FE-001: Browser MCP Activation**
- **Priority:** Medium
- **Effort:** Low (infrastructure complete)
- **Benefit:** Access to LMSAL flare data
- **Requirements:**
  - Claude Desktop with Chrome/Brave MCP configured
  - Filesystem MCP enabled
  - Browser running locally
- **Implementation:**
  - Activate enhanced_automation.py
  - Configure blocked sites list
  - Test browser fetch workflow
  - Integrate results into reports

**FE-002: PDF Generation**
- **Priority:** Low-Medium
- **Effort:** Low (dependencies commented out)
- **Benefit:** Printable, shareable reports
- **Requirements:**
  - Install reportlab or weasyprint
  - Add PDF conversion logic
  - Enable in config.yaml
- **Implementation:**
  - Uncomment PDF dependencies
  - Convert HTML to PDF
  - Save alongside other formats
  - Test rendering quality

**FE-003: Email Notifications**
- **Priority:** Medium
- **Effort:** Medium
- **Benefit:** Alerts for significant events
- **Requirements:**
  - SMTP credentials in .env
  - Email template creation
  - Alert threshold configuration
- **Implementation:**
  - Detect M-class flares, G2+ storms
  - Compose email from template
  - Send via SMTP
  - Log delivery status
  - Rate limit to avoid spam

**FE-004: Custom Alert Thresholds**
- **Priority:** Medium
- **Effort:** Medium
- **Benefit:** Personalized notifications
- **Requirements:**
  - Parse report for events
  - Compare to thresholds
  - Trigger notifications
- **Implementation:**
  - Extract flare classes from data
  - Extract Kp indices
  - Check against configured thresholds
  - Trigger alerts (email, push, etc.)

### 15.2 Medium-Term Enhancements

**FE-005: Historical Analysis**
- **Priority:** Medium
- **Effort:** High
- **Benefit:** Trend analysis, cycle tracking
- **Requirements:**
  - Database for report storage
  - Data extraction from JSON
  - Analysis algorithms
  - Visualization library
- **Features:**
  - Flare frequency over time
  - Sunspot number trends
  - Geomagnetic storm statistics
  - Solar cycle phase tracking
  - Monthly/yearly summaries
- **Implementation:**
  - SQLite database for reports
  - Extract key metrics from JSON
  - Generate trend charts
  - Add to reports or separate dashboard

**FE-006: Enhanced Visualizations**
- **Priority:** Medium
- **Effort:** Medium-High
- **Benefit:** Visual data representation
- **Requirements:**
  - matplotlib or plotly
  - Data parsing for metrics
  - Chart generation logic
  - HTML embedding
- **Features:**
  - Solar wind speed line chart
  - Kp index bar chart
  - Flare classification pie chart
  - Active region evolution
  - CME frequency histogram
- **Implementation:**
  - Generate charts from data
  - Save as PNG or SVG
  - Embed in HTML reports
  - Link in Markdown reports

**FE-007: Multi-User Support**
- **Priority:** Low-Medium
- **Effort:** High
- **Benefit:** Shared infrastructure
- **Requirements:**
  - User configuration profiles
  - Per-user output directories
  - Per-user preferences
  - Authentication (if shared system)
- **Features:**
  - Different users, different output formats
  - Custom alert thresholds per user
  - Shared data fetching
  - Individual report styling
- **Implementation:**
  - User profile YAML files
  - Directory structure: /users/{username}/reports/
  - Iterate users on each run
  - Generate per preferences

**FE-008: Mobile Notifications**
- **Priority:** Low
- **Effort:** High
- **Benefit:** Immediate awareness anywhere
- **Requirements:**
  - Push notification service (Pushover, IFTTT, etc.)
  - API credentials
  - Mobile app installation
- **Features:**
  - Push notifications for major events
  - Custom notification sound/priority
  - Rich notifications with details
  - Action buttons (view report, dismiss)
- **Implementation:**
  - Integrate Pushover or similar API
  - Send notification on threshold breach
  - Include summary in notification
  - Link to full report

### 15.3 Long-Term Vision

**FE-009: Machine Learning Integration**
- **Priority:** Low (research project)
- **Effort:** Very High
- **Benefit:** Predictive capability
- **Requirements:**
  - Historical data (months/years)
  - ML framework (TensorFlow, PyTorch)
  - Domain expertise
  - Significant compute resources
- **Features:**
  - Flare prediction from sunspot evolution
  - CME Earth-impact probability
  - Geomagnetic storm forecasting
  - Aurora visibility prediction
- **Implementation:**
  - Collect training data
  - Develop prediction models
  - Validate against actual events
  - Integrate into forecasts
  - Continuous learning

**FE-010: Real-Time Monitoring**
- **Priority:** Low
- **Effort:** Very High
- **Benefit:** Immediate event awareness
- **Requirements:**
  - Streaming architecture
  - Real-time data sources
  - WebSocket or similar
  - Always-running service
- **Features:**
  - Continuous data updates (not 6-hour)
  - Event detection within minutes
  - Real-time dashboard
  - Immediate alerts
- **Implementation:**
  - Switch to streaming data sources
  - Long-running service (not interval)
  - Event detection pipeline
  - WebSocket server for dashboard
  - Redis or similar for caching

**FE-011: Community Data Sharing**
- **Priority:** Low
- **Effort:** High
- **Benefit:** Citizen science contribution
- **Requirements:**
  - Web hosting
  - Public API
  - Data anonymization
  - Privacy considerations
- **Features:**
  - Public report archive
  - API for accessing data
  - Community contributions
  - Data visualization dashboard
- **Implementation:**
  - Web server for reports
  - RESTful API
  - Frontend dashboard
  - User contributions (observations)

**FE-012: Aurora Forecasting**
- **Priority:** Medium (high user interest)
- **Effort:** Medium-High
- **Benefit:** Practical aurora photography planning
- **Requirements:**
  - Location-based calculations
  - Geomagnetic data
  - Cloud cover integration
  - Astronomical calculations
- **Features:**
  - Location-specific aurora visibility
  - Optimal viewing times
  - Cloud cover forecast integration
  - Moon phase consideration
  - Historical aurora statistics
  - Photography tips
- **Implementation:**
  - Accept user location (lat/lon)
  - Calculate geomagnetic latitude
  - Integrate weather API
  - Calculate visibility probability
  - Generate viewing recommendations

### 15.4 Enhancement Prioritization

**High Priority (Next 3-6 months):**
1. Email notifications for major events
2. Custom alert thresholds
3. Browser MCP activation (if LMSAL access needed)

**Medium Priority (6-12 months):**
1. Historical analysis and trends
2. Enhanced visualizations (charts)
3. Aurora forecasting

**Low Priority (12+ months):**
1. PDF generation
2. Multi-user support
3. Mobile notifications
4. Community data sharing

**Research Projects (timeline uncertain):**
1. Machine learning predictions
2. Real-time monitoring architecture

---

## 16. Success Metrics

### 16.1 Operational Metrics

**Reliability:**
- **Target:** 99% successful report generation
- **Current:** 100% (recent runs)
- **Measurement:** Successful runs / Total scheduled runs
- **Tracking:** Log analysis, grep for "Successfully generated"

**Performance:**
- **Target:** <60 seconds total execution time
- **Current:** ~40 seconds average
- **Measurement:** Timestamp difference (start to completion)
- **Tracking:** Log timestamps, execution duration

**Data Source Availability:**
- **Target:** 90%+ success rate per source
- **Current:** 100% for all active sources
- **Measurement:** Successful fetches / Total attempts per source
- **Tracking:** Log analysis, grep for "Successfully fetched"

**API Success Rate:**
- **Target:** 95%+ successful Claude API calls
- **Current:** 100% (recent runs)
- **Measurement:** Successful API calls / Total attempts
- **Tracking:** Log analysis, grep for "enhanced Claude"

### 16.2 Quality Metrics

**Report Completeness:**
- **Target:** 100% of reports include all required sections
- **Measurement:** Manual spot-checking of generated reports
- **Required Sections:**
  - Headline with date range
  - Opening narrative
  - Flare activity
  - Sunspot regions
  - CME activity
  - Solar wind parameters
  - Geomagnetic conditions
  - 3-day forecast

**Link Quality:**
- **Target:** 100% of links are functional
- **Measurement:** Link checker on sample reports
- **Link Types:** 15+ different educational link types

**Technical Accuracy:**
- **Target:** 100% of numerical values match source data
- **Measurement:** Spot-check values against NOAA sources
- **Key Values:**
  - Flare times and classes
  - Active region numbers
  - Kp indices
  - Solar wind speed
  - IMF Bz

### 16.3 User Experience Metrics

**Installation Success:**
- **Target:** 95%+ users can complete setup in <10 minutes
- **Measurement:** User feedback, setup time tracking
- **Indicators:**
  - setup.sh completes without errors
  - Service loads successfully
  - First report generated

**Configuration Ease:**
- **Target:** 90%+ users understand config options
- **Measurement:** Documentation clarity, user questions
- **Indicators:**
  - Minimal support requests
  - Successful customization
  - Clear error messages

**Report Usability:**
- **Target:** 90%+ users find reports informative and readable
- **Measurement:** User feedback, qualitative assessment
- **Indicators:**
  - Reports read as natural language
  - Technical terms explained via links
  - Appropriate detail level

### 16.4 Cost Metrics

**Claude API Costs:**
- **Target:** <$10/month for typical usage
- **Current:** ~$6-8/month (4 runs/day)
- **Measurement:** Token usage tracking, Anthropic billing
- **Optimization:** Monitor and optimize prompt length

**Storage Costs:**
- **Target:** <100 MB for 30-day retention
- **Current:** ~80 MB (typical)
- **Measurement:** Disk usage (du -sh reports/)
- **Optimization:** Compress JSON, adjust retention

**Compute Costs:**
- **Target:** Minimal (local execution)
- **Current:** Negligible (<0.1% CPU average)
- **Measurement:** System resource monitoring
- **Optimization:** Not currently needed

### 16.5 Development Metrics

**Code Quality:**
- **Target:** Maintainable, well-documented code
- **Measurement:** Code review, documentation coverage
- **Indicators:**
  - All classes have docstrings
  - All public methods documented
  - PEP 8 compliance
  - Clear variable names

**Documentation Quality:**
- **Target:** Comprehensive, up-to-date documentation
- **Current:** 13 markdown files, 17.7 KB CLAUDE.md
- **Measurement:** Documentation coverage, user questions
- **Indicators:**
  - All features documented
  - Examples provided
  - Troubleshooting guides
  - Architecture diagrams

**Test Coverage:**
- **Target:** Critical paths tested (currently manual)
- **Current:** Manual testing, no automated tests
- **Future:** Implement unit tests for core functions
- **Measurement:** Test coverage percentage (future)

---

## 17. Technical Specifications

### 17.1 System Requirements

**Operating System:**
- **Primary:** macOS 10.14+ (Mojave or later)
- **Supported:** Linux (Ubuntu 18.04+, Debian 10+, etc.)
- **Possible:** Windows 10+ (with minor adjustments)

**Python:**
- **Required:** Python 3.7+
- **Recommended:** Python 3.9+
- **Tested:** Python 3.9
- **Required Tools:** pip3, venv (optional but recommended)

**Disk Space:**
- **Application:** ~1 MB
- **Dependencies:** ~50 MB
- **Reports (30 days):** ~50-100 MB (typical)
- **Logs:** ~10-50 MB (with rotation)
- **Total:** ~100-200 MB

**Memory:**
- **Runtime:** <100 MB
- **Peak:** ~150 MB (during Claude API call)
- **Idle:** ~5 MB (service waiting)

**Network:**
- **Outbound HTTPS:** Required
- **Bandwidth:** ~1-2 MB per run (data fetching + API)
- **Daily:** ~4-8 MB (4 runs)
- **Monthly:** ~120-240 MB
- **No inbound connections required**

### 17.2 Software Dependencies

**Core Python Packages:**
```
requests>=2.31.0              # HTTP client library
pyyaml>=6.0.1                 # YAML parser
schedule>=1.2.0               # Task scheduling
python-dotenv>=1.0.0          # Environment variables
anthropic>=0.39.0             # Claude API client
python-dateutil>=2.8.2        # Date/time utilities
pytz>=2023.3                  # Timezone support
```

**Optional Packages:**
```
reportlab>=4.0.0              # PDF generation (future)
weasyprint>=60.0              # Alternative PDF (future)
matplotlib>=3.5.0             # Visualizations (future)
pytest>=7.0.0                 # Testing (future)
```

**System Dependencies:**
- **macOS:** None (all in Python)
- **Linux:** May need libssl-dev for some packages
- **Windows:** May need Visual C++ for some packages

### 17.3 External Service Dependencies

**Required:**
- **Anthropic Claude API:** claude-sonnet-4-20250514
- **NOAA SWPC:** https://services.swpc.noaa.gov
- **Internet connectivity:** Broadband (1+ Mbps)

**Recommended:**
- **UK Met Office:** https://weather.metoffice.gov.uk
- **SpaceWeather.com:** https://www.spaceweather.com
- **EarthSky.org:** https://earthsky.org
- **SpaceWeatherLive.com:** https://www.spaceweatherlive.com

**Optional:**
- **Claude Desktop:** For Browser MCP integration
- **Chrome/Brave Browser:** For browser automation
- **Obsidian:** For viewing Markdown reports

### 17.4 File System Structure

```
space-weather-reports/
├── space_weather_automation.py       # Main application
├── claude_integration_enhanced.py    # Claude integration
├── scheduler.py                      # Foreground scheduler
├── setup.sh                          # Setup script
├── config.yaml                       # Configuration
├── .env                              # Secrets (API keys)
├── .env.example                      # Template
├── .gitignore                        # Git exclusions
├── requirements.txt                  # Dependencies
├── README.md                         # User documentation
├── CLAUDE.md                         # Developer guide
├── PRD.md                            # This document
├── space_weather_automation.log      # Main log
├── stdout.log                        # launchd stdout
├── stderr.log                        # launchd stderr
├── test_run.log                      # Test output
│
├── code/                             # Alternative implementations
│   ├── README.md
│   ├── enhanced_automation.py
│   ├── browser_mcp_workflow.py
│   ├── browser_mcp_fetcher.py
│   ├── browser_scraping.py
│   ├── claude_integration.py
│   ├── auto_integrate.py
│   └── INTEGRATION_GUIDE.py
│
├── docs/                             # Documentation
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── API_KEY_SETUP.md
│   ├── AUTOMATION_COMPLETE.md
│   ├── BROWSER_MCP_SOLUTION.md
│   ├── BROWSER_MCP_GUIDE.md
│   ├── BROWSER_SCRAPING_GUIDE.md
│   ├── REPORT_STYLE_GUIDE.md
│   ├── REPORT_QUALITY_ANALYSIS.md
│   ├── ENV_SETUP_COMPLETE.md
│   └── COMPLETE_ANSWER.md
│
└── reports/                          # Generated reports
    ├── README.md
    ├── space_weather_2025-11-02_1643.html
    ├── space_weather_2025-11-02_1643.md
    ├── space_weather_2025-11-02_1643.json
    ├── space_weather_2025-11-02_1643.txt
    └── [... more reports ...]
```

### 17.5 Network Ports & Protocols

**Outbound Connections:**
- **HTTPS (443):** All external data fetching and API calls
- **HTTP (80):** None (all upgraded to HTTPS)

**Inbound Connections:**
- **None required:** System operates entirely outbound

**Firewall Requirements:**
- **Outbound HTTPS:** Must be allowed
- **No inbound rules needed**

### 17.6 Performance Characteristics

**Execution Times (typical):**
- Data fetching: 3-10 seconds
- Claude API call: 25-40 seconds
- Format conversion: <1 second
- File saving: <1 second
- Cleanup: <1 second
- **Total: 30-50 seconds**

**Resource Usage:**
- CPU: <5% during execution (single core)
- Memory: 50-150 MB during execution
- Disk I/O: Minimal (small file writes)
- Network: 1-2 MB per run

**Scalability:**
- Current: Single user, 4 runs/day
- Potential: 10+ users, 24+ runs/day per user
- Bottleneck: Claude API rate limits (not yet reached)
- Scaling strategy: Multi-threading for multiple users

---

## 18. Deployment & Operations

### 18.1 Installation Process

**One-Command Setup (macOS):**
```bash
./setup.sh
```

**Manual Setup (all platforms):**
```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Configure API key
cp .env.example .env
nano .env  # Add your API key

# 3. Customize configuration
nano config.yaml  # Adjust paths, preferences

# 4. Test run
python3 space_weather_automation.py

# 5. Setup automation
# macOS: Run setup.sh
# Linux: Add to crontab
# Windows: Add to Task Scheduler
```

**Installation Verification:**
```bash
# Check dependencies
pip3 list | grep -E 'requests|pyyaml|anthropic|schedule|dotenv|dateutil|pytz'

# Check configuration
cat config.yaml

# Check API key (without revealing it)
grep -c ANTHROPIC_API_KEY .env

# Test execution
python3 space_weather_automation.py

# Check for reports
ls -lh reports/

# Check logs
tail -n 20 space_weather_automation.log
```

### 18.2 Configuration Steps

**1. API Key Setup:**
```bash
# Copy template
cp .env.example .env

# Edit file
nano .env

# Add key
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here

# Secure file
chmod 600 .env
```

**2. Output Directory:**
```yaml
# config.yaml
output:
  base_directory: "/path/to/your/obsidian/vault/space-weather-reports/reports"
```

**3. Schedule Adjustment:**
```yaml
# config.yaml
schedule:
  interval_hours: 6  # Change to 3, 12, 24, etc.
  # OR
  specific_times: ["00:00", "06:00", "12:00", "18:00"]  # Specific times
```

**4. Output Formats:**
```yaml
# config.yaml
output:
  formats:
    html: true       # Set to false to disable
    markdown: true
    json: false      # Disable large JSON files if not needed
    text: true
```

### 18.3 Service Management

**macOS (launchd):**
```bash
# Start service
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist

# Stop service
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist

# Check status
launchctl list | grep spaceweather

# Restart service
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist

# View service configuration
cat ~/Library/LaunchAgents/com.user.spaceweather.plist
```

**Linux (cron):**
```bash
# Edit crontab
crontab -e

# Add line for every 6 hours
0 */6 * * * cd /path/to/space-weather-reports && /usr/bin/python3 space_weather_automation.py

# List current jobs
crontab -l

# Remove job
crontab -e  # Delete the line
```

**Windows (Task Scheduler):**
```powershell
# Via GUI: Task Scheduler > Create Basic Task
# Name: Space Weather Reports
# Trigger: Daily, repeat every 6 hours
# Action: Start a program
# Program: python
# Arguments: space_weather_automation.py
# Start in: C:\path\to\space-weather-reports
```

### 18.4 Monitoring & Maintenance

**Daily Checks:**
```bash
# Check last run time
ls -lt reports/*.html | head -n 1

# Check for recent errors
grep ERROR space_weather_automation.log | tail -n 10

# Verify service running
launchctl list | grep spaceweather
```

**Weekly Checks:**
```bash
# Review success rate
grep "Successfully generated" space_weather_automation.log | wc -l

# Check disk usage
du -sh reports/

# Review log size
ls -lh space_weather_automation.log
```

**Monthly Maintenance:**
```bash
# Update dependencies
pip3 install --upgrade -r requirements.txt

# Review configuration
cat config.yaml

# Test manual run
python3 space_weather_automation.py

# Archive old logs (optional)
mv space_weather_automation.log.5 archive/
```

### 18.5 Troubleshooting

**No reports generated:**
```bash
# Check service status
launchctl list | grep spaceweather

# Check for errors
tail -n 50 space_weather_automation.log

# Try manual run
python3 space_weather_automation.py

# Check permissions
ls -la reports/
```

**Reports incomplete:**
```bash
# Check API key
grep -c ANTHROPIC_API_KEY .env

# Check for API errors
grep "Claude" space_weather_automation.log | tail -n 10

# Check data source errors
grep "fetch" space_weather_automation.log | tail -n 10
```

**Service not running:**
```bash
# Reload service
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist

# Check stderr log
cat stderr.log

# Verify Python path
which python3

# Update plist with correct path
nano ~/Library/LaunchAgents/com.user.spaceweather.plist
```

**Disk space issues:**
```bash
# Check current usage
du -sh reports/

# Reduce retention
# Edit config.yaml, set max_archive_days to lower value

# Manual cleanup
find reports/ -mtime +30 -delete
```

### 18.6 Backup & Recovery

**Configuration Backup:**
```bash
# Backup configuration files
cp config.yaml config.yaml.backup
cp .env .env.backup

# Or create archive
tar -czf spaceweather-config-$(date +%Y%m%d).tar.gz config.yaml .env
```

**Report Backup:**
```bash
# Backup all reports
tar -czf spaceweather-reports-$(date +%Y%m%d).tar.gz reports/

# Or sync to cloud storage
rsync -av reports/ ~/Dropbox/space-weather-archive/
```

**Recovery:**
```bash
# Restore configuration
cp config.yaml.backup config.yaml
cp .env.backup .env

# Restore reports
tar -xzf spaceweather-reports-20251102.tar.gz

# Restart service
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist
```

### 18.7 Upgrade Process

**Minor Updates (configuration, documentation):**
```bash
# Pull latest changes
git pull origin main

# Review changes
git log

# No service restart needed for docs
# Restart only if config changed
```

**Major Updates (code changes):**
```bash
# Stop service
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist

# Backup current version
cp space_weather_automation.py space_weather_automation.py.backup

# Pull updates
git pull origin main

# Update dependencies if needed
pip3 install --upgrade -r requirements.txt

# Test manually
python3 space_weather_automation.py

# Restart service
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist

# Monitor logs
tail -f space_weather_automation.log
```

**Rollback:**
```bash
# Stop service
launchctl unload ~/Library/LaunchAgents/com.user.spaceweather.plist

# Restore backup
cp space_weather_automation.py.backup space_weather_automation.py

# Restart service
launchctl load ~/Library/LaunchAgents/com.user.spaceweather.plist
```

---

## Appendix A: Glossary

**Active Region (AR):** Numbered sunspot region with magnetic complexity

**CME:** Coronal Mass Ejection - massive burst of solar material

**G-Scale:** Geomagnetic storm scale (G1-G5, G5 strongest)

**IMF:** Interplanetary Magnetic Field

**Kp Index:** Global geomagnetic activity index (0-9)

**launchd:** macOS background service manager

**LMSAL:** Lockheed Martin Solar and Astrophysics Laboratory

**MCP:** Model Context Protocol - for AI tool use

**NOAA SWPC:** National Oceanic and Atmospheric Administration Space Weather Prediction Center

**R-Scale:** Radio blackout scale (R1-R5, R5 strongest)

**Solar Flare Classes:**
- C-class: Common, minor
- M-class: Moderate, can cause radio blackouts
- X-class: Strongest, major impacts

**UTC:** Coordinated Universal Time

---

## Appendix B: References

**Official Sources:**
- NOAA SWPC: https://www.swpc.noaa.gov/
- UK Met Office: https://www.metoffice.gov.uk/weather/specialist-forecasts/space-weather

**Educational Resources:**
- EarthSky: https://earthsky.org/sun/
- SpaceWeather.com: https://www.spaceweather.com/
- SpaceWeatherLive: https://www.spaceweatherlive.com/

**Technical Documentation:**
- Anthropic Claude API: https://docs.anthropic.com/
- Python Requests: https://docs.python-requests.org/
- PyYAML: https://pyyaml.org/
- Obsidian: https://obsidian.md/

**Project Documentation:**
- README.md - User guide
- CLAUDE.md - Developer architecture guide
- docs/ - Comprehensive documentation collection

---

## Appendix C: Change Log

**Version 1.0 (November 2, 2025):**
- Initial PRD creation
- Complete codebase analysis (2,754 lines)
- Production system documented
- All features and capabilities documented
- Future enhancements identified

---

## Document Approval

**Prepared By:** Automated System Analysis
**Review Date:** November 2, 2025
**Status:** Production System - Fully Operational
**Next Review:** As needed for major updates

---

**End of Product Requirements Document**
