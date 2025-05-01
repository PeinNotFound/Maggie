import discord
import os
import logging
from nudenet import NudeDetector
import shutil
from datetime import datetime

# Replace with your actual bot token
TOKEN = ''

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Create image storage directories
image_directory = "captured_images"
archived_directory = "archived_images"
os.makedirs(image_directory, exist_ok=True)
os.makedirs(archived_directory, exist_ok=True)

# Initialize NudeNet detector
detector = NudeDetector()

# Function to get or create the logs channel
async def get_or_create_logs_channel(guild):
    for channel in guild.text_channels:
        if channel.name == "logs":
            return channel
    logs_channel = await guild.create_text_channel('logs')
    return logs_channel

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    for attachment in message.attachments:
        if attachment.content_type and attachment.content_type.startswith("image/"):
            image_path = os.path.join(image_directory, attachment.filename)
            await attachment.save(image_path)
            logging.info(f"📥 Saved image to {image_path}")

            try:
                # Check if the image exists in captured_images
                if os.path.exists(image_path):
                    logging.info(f"✅ Image exists in captured_images: {image_path}")
                else:
                    logging.error(f"❌ Image not found in captured_images: {image_path}")

                # Run detection
                detections = detector.detect(image_path)
                logging.info(f"🚨 RAW detection output: {detections}")  # Print raw output

                # NSFW detection logic with stricter thresholds
                nsfw_labels = ["EXPOSED_BREASTS", "EXPOSED_GENITALS", "EXPOSED_ANUS", "EXPOSED"]
                for item in detections:
                    label = item.get("class")
                    score = item.get("score", 0)
                    print("🧠 Label:", label, "Score:", score)  # Debug output

                    # Check for label "EXPOSED" and score > 0.5
                    if "EXPOSED" in label and score > 0.5:
                        # Delete the message
                        await message.delete()

                        # Send a warning message in the current channel
                        await message.channel.send(
                            f"⚠️ NSFW content from {message.author.mention} was removed. Detected: {label} ({score:.2f})"
                        )

                        # Send the violation details to the logs channel
                        logs_channel = await get_or_create_logs_channel(message.guild)
                        await logs_channel.send(
                            f"⚠️ **NSFW violation detected!**\n"
                            f"**User**: {message.author.mention}\n"
                            f"**Message**: {message.content[:50]}...\n"
                            f"**Detection**: {label} with score {score:.2f}\n"
                            f"**Link**: {message.jump_url}"
                        )

                        # Archive the image with a new name based on user ID, label, and timestamp
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        archived_filename = f"{message.author.id}_{label}_{timestamp}_{attachment.filename}"
                        archived_image_path = os.path.join(archived_directory, archived_filename)

                        # Move the image to the archive
                        shutil.move(image_path, archived_image_path)
                        logging.info(f"🗄️ Archived image to {archived_image_path}")

                        break
                else:
                    logging.info("✅ Image is safe.")
            
            except Exception as e:
                logging.error(f"❌ Detection failed: {e}")
            
            # The image is no longer removed, since it's archived permanently
            # No need to remove it here anymore

# Run the bot
client.run(TOKEN)
