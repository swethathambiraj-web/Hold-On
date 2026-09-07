import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from accounts.models import User, Follow
from posts.models import Post, PostMedia, Hashtag, Like, Comment, SavedPost
from stories.models import Story, StoryView
from notifications.models import Notification
from messaging.models import Conversation, Message


class Command(BaseCommand):
    help = 'Seeds the database with sample demo users, posts, stories, comments, and messages for Hold On'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding demo data for Hold On social media app...")

        # 1. Create Demo Users
        users_data = [
            {
                'username': 'alex_wanderer',
                'email': 'alex@example.com',
                'first_name': 'Alex',
                'last_name': 'Rivers',
                'bio': '🌲 Landscape photographer & mountaineer\n📍 Pacific Northwest\n📷 Shooting on Sony A7IV\n✉️ alex@wanders.io',
                'website_link': 'https://alexrivers.photo',
                'is_private': False,
            },
            {
                'username': 'maya_design',
                'email': 'maya@example.com',
                'first_name': 'Maya',
                'last_name': 'Lin',
                'bio': '✨ Digital Artist & UI/UX Designer\n🎨 Creating whimsical cyberpunk worlds\n☕ Coffee addict | London 🇬🇧',
                'website_link': 'https://mayalin.design',
                'is_private': False,
            },
            {
                'username': 'chef_marco',
                'email': 'marco@example.com',
                'first_name': 'Marco',
                'last_name': 'Rossi',
                'bio': '🍝 Head Chef @ Osteria Bella\n🍕 Woodfired pizza & artisanal pasta\n🍷 Florence • New York',
                'website_link': 'https://osteriamarco.com',
                'is_private': False,
            },
            {
                'username': 'sophia_code',
                'email': 'sophia@example.com',
                'first_name': 'Sophia',
                'last_name': 'Chen',
                'bio': '💻 AI Research & Python engineer\n🚀 Building the future of neural interfaces\n📚 Tech book author',
                'website_link': 'https://sophiachen.ai',
                'is_private': False,
            },
            {
                'username': 'leo_vibes',
                'email': 'leo@example.com',
                'first_name': 'Leo',
                'last_name': 'Vance',
                'bio': '🛹 Streetwear, vinyl records & analog film\n🌆 Tokyo vibes',
                'website_link': 'https://leovance.jp',
                'is_private': True,
            },
        ]

        created_users = {}
        for udata in users_data:
            user, created = User.objects.get_or_create(
                username=udata['username'],
                defaults={
                    'email': udata['email'],
                    'first_name': udata['first_name'],
                    'last_name': udata['last_name'],
                    'bio': udata['bio'],
                    'website_link': udata['website_link'],
                    'is_private': udata['is_private'],
                }
            )
            user.set_password('password123')
            user.save()
            created_users[udata['username']] = user

        # 2. Create Follow Relationships
        alex = created_users['alex_wanderer']
        maya = created_users['maya_design']
        marco = created_users['chef_marco']
        sophia = created_users['sophia_code']
        leo = created_users['leo_vibes']

        follows = [
            (alex, maya, 'accepted'),
            (alex, marco, 'accepted'),
            (alex, sophia, 'accepted'),
            (maya, alex, 'accepted'),
            (maya, sophia, 'accepted'),
            (marco, alex, 'accepted'),
            (sophia, alex, 'accepted'),
            (sophia, maya, 'accepted'),
            (alex, leo, 'pending'), # pending for private user
            (sophia, leo, 'accepted'),
        ]

        for follower, following, status in follows:
            Follow.objects.get_or_create(
                follower=follower,
                following=following,
                defaults={'status': status}
            )

        # 3. Create Sample Posts
        posts_data = [
            {
                'author': alex,
                'caption': 'Sunrise at Mount Rainier after an 8-hour midnight trek. The colors were completely unreal. #hiking #nature #mountains #photography #adventure',
                'location': 'Mount Rainier National Park, WA',
                'image_urls': [
                    'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80',
                    'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80'
                ]
            },
            {
                'author': maya,
                'caption': 'Finished the latest 3D render exploring neon brutalism. What do you guys think of this color palette? 🎨💜 #digitalart #design #cyberpunk #3drender #uiux',
                'location': 'Soho Studio, London',
                'image_urls': [
                    'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80'
                ]
            },
            {
                'author': marco,
                'caption': 'Handmade tagliatelle with slow-simmered wild mushroom ragù and 24-month Parmigiano Reggiano. Pure comfort food on a chilly evening. 🍝🧀 #italianfood #pasta #chef #foodie #cooking',
                'location': 'Osteria Bella, Florence',
                'image_urls': [
                    'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=1200&q=80',
                    'https://images.unsplash.com/photo-1546549032-9571cd6b27df?auto=format&fit=crop&w=1200&q=80'
                ]
            },
            {
                'author': sophia,
                'caption': 'Late night coding session running multi-modal transformer fine-tuning. Beautiful loss curve convergence makes everything worth it! 🚀⚡ #python #ai #datascience #coding #tech',
                'location': 'Silicon Valley, CA',
                'image_urls': [
                    'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80'
                ]
            }
        ]

        import urllib.request
        for pdata in posts_data:
            post, p_created = Post.objects.get_or_create(
                author=pdata['author'],
                caption=pdata['caption'],
                defaults={'location': pdata['location']}
            )
            if p_created:
                post.extract_hashtags()
                for idx, img_url in enumerate(pdata['image_urls']):
                    try:
                        req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            img_content = resp.read()
                            filename = f"post_{post.id}_{idx}.jpg"
                            media = PostMedia(post=post, media_type='image', order=idx)
                            media.file.save(filename, ContentFile(img_content), save=True)
                    except Exception as e:
                        # Fallback if offline
                        pass

                # Add likes
                for liker in [alex, maya, marco, sophia]:
                    if liker != post.author:
                        Like.objects.get_or_create(user=liker, post=post)

                # Add comments
                if post.author == alex:
                    Comment.objects.create(user=maya, post=post, text="This is breathtaking Alex! What lens did you use?")
                    Comment.objects.create(user=marco, post=post, text="Incredible lighting! 🔥")
                elif post.author == maya:
                    Comment.objects.create(user=sophia, post=post, text="The neon glow contrast is pristine! Love it ✨")
                elif post.author == marco:
                    Comment.objects.create(user=alex, post=post, text="Looks delicious Chef! Need to visit next time I'm in Italy 😋")

        # 4. Create Sample Active Stories
        stories_data = [
            {
                'user': alex,
                'caption': 'Morning mist over the lake 🌄',
                'url': 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=800&q=80'
            },
            {
                'user': maya,
                'caption': 'Work in progress sketches ✍️',
                'url': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80'
            },
            {
                'user': marco,
                'caption': 'Fresh truffles just arrived from Piedmont! 🍄',
                'url': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80'
            }
        ]

        for sdata in stories_data:
            story = Story.objects.create(
                user=sdata['user'],
                caption=sdata['caption'],
                expires_at=timezone.now() + timedelta(hours=24)
            )
            try:
                req = urllib.request.Request(sdata['url'], headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    img_content = resp.read()
                    filename = f"story_{story.id}.jpg"
                    story.media.save(filename, ContentFile(img_content), save=True)
            except Exception:
                pass

        # 5. Create Direct Message Conversation
        conv, _ = Conversation.objects.get_or_create(id=1)
        conv.participants.set([alex, maya])
        Message.objects.get_or_create(
            conversation=conv,
            sender=maya,
            text='Hey Alex! Are you going to the photography gallery opening this Friday?',
            defaults={'is_read': True}
        )
        Message.objects.get_or_create(
            conversation=conv,
            sender=alex,
            text='Hey Maya! Yes, definitely. Let’s grab coffee beforehand!',
            defaults={'is_read': True}
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded demo data!"))
        self.stdout.write("Demo accounts created (Password for all is 'password123'):")
        self.stdout.write(" - alex_wanderer")
        self.stdout.write(" - maya_design")
        self.stdout.write(" - chef_marco")
        self.stdout.write(" - sophia_code")
        self.stdout.write(" - leo_vibes (private account)")
