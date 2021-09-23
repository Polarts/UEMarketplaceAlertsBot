# UEMarketplaceAlertsBot

A Facebook bot that scrapes Unreal Marketplace for weekly updates on new free assets.

Based on [jhinter](https://github.com/jhinter)'s [article on medium.com](https://medium.com/p/54e88b3ebd42)

The app consists of 2 main components that share a database.

### 1. Django: the admin panel

Defined and manages the database, monitors and controls the bot process.

### 2. The bot: a scheduled, repeating task

Responsible for scraping, persisting and posting alerts of new assets on UE Marketplace. 
