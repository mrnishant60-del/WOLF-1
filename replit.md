# Wolf Discord Bot - Replit Environment

## Project Overview

Wolf is an open-source Discord bot designed for esports server management. It provides automated scrims, tournament management, and community engagement tools.

**Last Updated:** October 18, 2025

## Project Architecture

### Technology Stack
- **Language:** Python 3.11
- **Framework:** discord.py 2.3.0
- **Database:** PostgreSQL (via Replit's built-in database)
- **ORM:** Tortoise ORM 0.19.3
- **Migrations:** Aerich 0.7.1
- **Web Framework:** FastAPI 0.98.0 (for payment/API endpoints)
- **WebSockets:** python-socketio 5.8.0

### Project Structure
```
src/
├── bot.py              # Main entry point
├── config.py           # Configuration (auto-generated from example_config.py)
├── constants.py        # Bot constants and utilities
├── cogs/              # Discord bot command modules
│   ├── esports/       # Esports management features (scrims, tournaments)
│   ├── events/        # Event handlers and tasks
│   ├── mod/           # Moderation features
│   ├── premium/       # Premium subscription features
│   ├── quomisc/       # Miscellaneous commands
│   ├── reminder/      # Reminder system
│   └── utility/       # Utility commands
├── core/              # Core bot classes (Bot, Context, Help)
├── models/            # Database models (Tortoise ORM)
├── server/            # FastAPI server for payments
├── sockets/           # SocketIO server for dashboard
└── utils/             # Utility functions

data/                  # Static assets (fonts, images)
tests/                 # Test files
```

## Recent Changes

### October 18, 2025 - Premium User Access to Premium Features
- **Premium User Support:** Premium users can now access all premium features, not just premium guilds
  - Added `is_premium_user_or_guild()` check function in utils/checks.py
  - Added helper methods `is_premium_user()` and `is_premium_user_or_guild()` to Bot.py and Context.py
  - Updated wptable command to require either premium user or premium guild
  - Updated all premium-only features to allow both premium users and premium guilds:
    - IDP Transfer feature (slot manager)
    - Cancel Reminder feature (slot manager)
    - Multiple EasyTag channels (1+ channels)
    - Multiple TagCheck channels (1+ channels)
    - Multiple SSVerify setups (1+ setups)
    - Multiple Scrim creation (3+ scrims)
    - Multiple Tournament creation (1+ tournaments)
    - Multiple Slot Manager channels (1+ channels)
    - Custom scrim/tournament emojis
    - Minimum lines requirement for registrations
    - Duplicate tag allowance
    - Custom SSVerify filters
    - Multiple media partners for tournaments
    - Webhook publishing for group lists
  - All premium checks now display messages like "Either you or your server needs Wolf Premium" instead of guild-only restrictions

### October 18, 2025 - Points Table Image Enhancements
- **Scrims/Tournament Selection:** Users can now choose between "Scrims" or "Tournament" when generating images
  - "Tournament" selection creates image with "Tournament Point Table" heading
  - "Scrims" selection creates image with "Scrims Point Table" heading
  - Selection appears before image generation for both Create Image and Send Image buttons
- **Send Image Feature:** Added new "Send Image" button to send generated images to specific channels
  - User selects table type (Scrims/Tournament)
  - Image is generated with appropriate heading
  - User then selects which channel to send the image to
  - Similar flow to slotlist channel selection

### October 18, 2025 - Slotlist Fix
- **Slotlist Reverted to Embed Version:** Fixed slotlist to use the simpler embed-based display
  - Removed template image functionality (create_slotlist_template_img)
  - Slotlist now uses the original embed format with create_slotlist()
  - Cleaner and more reliable slotlist display
- **Cleanup:** Removed slotlist-related PNG files (slotlist_template.png, slotlist_output.png, slotlist_base.png, slot-rect.png)

### October 18, 2025 - Team Logo Integrated into Add Team Flow
- Integrated logo upload directly into the "Add Team" workflow
- After adding team details, users are prompted to upload a logo
- Streamlined user experience with unified team creation
- Features:
  - Upload logo images (PNG, JPG, GIF) via Discord attachment
  - Alternative: Provide logo URL
  - Option to skip logo and add team without it
  - Logos automatically downloaded and displayed in generated images
  - 60-second timeout for logo upload
  - No separate button needed - everything in one flow

### October 18, 2025 - Points Table Image Generation Fixed
- Fixed "Create Image" button in points table feature
- Implemented full image generation using PIL with custom backgrounds
- Features:
  - Generates professional tournament points table images
  - Uses random background templates from 20 available designs
  - Includes team rankings, kills, placement points, and chicken dinners
  - Displays team logos next to team names in generated images
  - Adds custom header and footer text to images
  - Watermark support for branding
  - Images sent privately to the user who creates them

### October 18, 2025 - Points Table Feature Activated
- Activated the points table command for tournament management
- Added `wptable`, `wpointstable`, and `wpt` commands
- Fixed PointsTable view implementation (team removal logic, modal handling, error handling)
- Features include:
  - Interactive team management (add/remove teams)
  - Track kills, placement points, and total scores
  - Customizable title and footer
  - Multi-select team removal support
  - "Send Table" button to select channel for posting
  - "Create Image" button for professional table graphics
  - Accessible via help panel under Esports commands

### October 17, 2025 - Branding Update
- Changed bot prefix from `q` to `w`
- Updated bot status to "whelp w setup"
- Replaced "Quo Coins" with "Wolf Coins" throughout the codebase
- Updated footer from "quo is lub!" to "wolf is lub!"
- Changed support server link to https://discord.gg/qXNWfdJpFd
- Removed bot invite, dashboard, website, and repository links from code
- Removed source, invite, vote, dashboard, and contributors commands
- Added developer/owner ID: 985731890193502269

### October 2, 2025 - Initial Replit Setup
- Created `config.py` from `example_config.py` to work with environment variables
- Configured PostgreSQL connection using Replit's built-in database
- Fixed Tortoise ORM connection string (postgresql:// → postgres://)
- Removed `sslmode` parameter from DATABASE_URL for asyncpg compatibility
- Installed all Python dependencies from requirements.txt
- Configured workflow to run the bot
- Set up project to use environment variables for secrets
- Successfully tested bot connection to Discord

## Setup Instructions

### Prerequisites
This bot requires a Discord application with a bot token. You'll need to:
1. Create a Discord application at https://discord.com/developers/applications
2. Create a bot user for your application
3. Copy the bot token

### Required Environment Variables

**Essential:**
- `DISCORD_TOKEN` - Your Discord bot token (required to run the bot)

**Optional:**
- `DEVS` - Comma-separated list of Discord user IDs who have bot owner permissions
- `ERROR_LOG` - Discord webhook URL for error logging
- `SHARD_LOG` - Discord webhook URL for shard logging
- `PUBLIC_LOG` - Discord webhook URL for public event logging
- `SERVER_LINK` - Discord server invite link (default: https://discord.gg/qXNWfdJpFd)

**Database:**
- `DATABASE_URL`, `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` - Automatically provided by Replit's PostgreSQL database

### How to Run

1. **Set up the database** (if not already done):
   - Create a PostgreSQL database using the Database tool in Replit's left sidebar
   - The database credentials will be automatically set as environment variables

2. **Add your Discord token**:
   - Go to the Secrets tool in Replit (Tools → Secrets)
   - Add a secret with key `DISCORD_TOKEN` and your bot token as the value

3. **Run the bot**:
   - Click the "Run" button or use the workflow panel
   - The bot will automatically:
     - Connect to the database
     - Generate database schemas
     - Load all cogs/extensions
     - Connect to Discord

4. **Invite the bot to your server**:
   - Use Discord's OAuth2 URL generator with the bot scope
   - Required permissions: Administrator (or the specific permissions listed in Bot.py)

## Database Management

The bot uses Tortoise ORM with Aerich for migrations. The database schema is automatically generated on first run via `Tortoise.generate_schemas(safe=True)`.

**Models include:**
- Guild settings and premium status
- Scrims and tournament configurations
- User data and timers
- Tag checks and slot managers
- Autoroles, lockdowns, and autopurge settings

## Extensions/Cogs Loaded

The bot loads the following extensions on startup:
- `cogs.events` - Core event handlers
- `cogs.esports` - Esports management (scrims/tournaments)
- `cogs.esports.slash` - Slash command versions
- `cogs.mod` - Moderation tools
- `cogs.premium` - Premium features
- `cogs.quomisc` - Miscellaneous utilities
- `cogs.reminder` - Reminder system
- `cogs.utility` - Utility commands
- `jishaku` - Bot debugging and development tools

## Configuration

The `config.py` file is auto-generated and uses environment variables. Key settings:
- **Prefix:** `w` (customizable per-guild)
- **Color:** `0x00FFB3` (customizable for premium guilds)
- **Footer:** "wolf is lub!" (customizable for premium guilds)
- **Timezone:** Asia/Kolkata (IST)

## Notes

- This is an **educational source** - the original developers prefer you use the hosted instance
- The bot requires specific intents: members, message_content, and default intents
- Database migrations are in `.gitignore` as they're generated per environment
- `config.py` is in `.gitignore` to protect secrets

## Support

- GitHub Repository: https://github.com/wolfbot/Wolf-Bot
- Discord Support Server: https://discord.gg/qXNWfdJpFd
- Official Website: https://wolfbot.xyz

## License

This project is licensed under the MPL-2.0 license.
