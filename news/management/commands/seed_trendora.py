import json
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import UserProfile
from news.models import NewsCategory, NewsSource, NewsArticle, SavedArticle
from trends.models import TrendingTopic

class Command(BaseCommand):
    help = 'Seeds TRENDORA with foundational categories, sources, trending topics, articles, and a demo analyst user.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing TRENDORA Intelligence Database Seed..."))

        # 1. Categories
        categories_data = [
            {
                'name': 'Technology & Computing',
                'slug': 'technology',
                'icon': 'cpu',
                'color_code': '#8b5cf6',
                'badge_class': 'badge-purple',
                'description': 'Frontier artificial intelligence, neuromorphic chips, quantum circuits, and cyber systems.',
                'order': 1,
            },
            {
                'name': 'Business & Financial Flows',
                'slug': 'business',
                'icon': 'brief',
                'color_code': '#06b6d4',
                'badge_class': 'badge-cyan',
                'description': 'Macroeconomic liquidity, venture capitalization, institutional debt, and algorithmic markets.',
                'order': 2,
            },
            {
                'name': 'Politics & Global Policy',
                'slug': 'politics',
                'icon': 'globe',
                'color_code': '#ec4899',
                'badge_class': 'badge-pink',
                'description': 'Geopolitical treaties, sovereign regulatory frameworks, and international security accords.',
                'order': 3,
            },
            {
                'name': 'Sports & High-Performance',
                'slug': 'sports',
                'icon': 'trophy',
                'color_code': '#f59e0b',
                'badge_class': 'badge-amber',
                'description': 'Biometric performance analytics, global championships, telemetry, and sporting economies.',
                'order': 4,
            },
            {
                'name': 'Science & Quantum Systems',
                'slug': 'science',
                'icon': 'orbit',
                'color_code': '#10b981',
                'badge_class': 'badge-emerald',
                'description': 'Nuclear fusion, orbital aerospace, genomics, CRISPR therapies, and astrophysics.',
                'order': 5,
            },
            {
                'name': 'Entertainment & Digital Media',
                'slug': 'entertainment',
                'icon': 'film',
                'color_code': '#f43f5e',
                'badge_class': 'badge-rose',
                'description': 'Generative cinema, virtual spatial computing, streaming dynamics, and gaming platforms.',
                'order': 6,
            },
        ]

        cat_map = {}
        for cdata in categories_data:
            cat, _ = NewsCategory.objects.update_or_create(
                slug=cdata['slug'],
                defaults=cdata
            )
            cat_map[cdata['slug']] = cat
        self.stdout.write(self.style.SUCCESS(f"Categories synchronized: {len(cat_map)} categories ready."))

        # 2. News Sources
        sources_data = [
            {'name': 'MIT Technology Review', 'domain': 'technologyreview.com', 'badge_color': '#8b5cf6'},
            {'name': 'Bloomberg Terminal Wire', 'domain': 'bloomberg.com', 'badge_color': '#06b6d4'},
            {'name': 'Reuters Intelligence', 'domain': 'reuters.com', 'badge_color': '#ec4899'},
            {'name': 'Nature Quantum Review', 'domain': 'nature.com', 'badge_color': '#10b981'},
            {'name': 'The Financial Times', 'domain': 'ft.com', 'badge_color': '#38bdf8'},
            {'name': 'Wired Strategic Dispatch', 'domain': 'wired.com', 'badge_color': '#a855f7'},
        ]

        src_map = {}
        for sdata in sources_data:
            slug = slugify(sdata['name'])
            src, _ = NewsSource.objects.update_or_create(
                name=sdata['name'],
                defaults={
                    'slug': slug,
                    'domain': sdata['domain'],
                    'url': f"https://{sdata['domain']}",
                    'badge_color': sdata['badge_color'],
                }
            )
            src_map[sdata['name']] = src
        self.stdout.write(self.style.SUCCESS(f"News sources synchronized: {len(src_map)} sources ready."))

        # 3. Trending Topics
        topics_data = [
            {
                'title': 'Autonomous AI Agents',
                'slug': 'autonomous-ai-agents',
                'category': cat_map['technology'],
                'volume_mentions': 48920,
                'velocity_percentage': 342,
                'sentiment': 'bullish',
                'trend_direction': 'hot',
                'movement_text': '+18 ranks today',
                'article_count': 124,
                'is_hot': True,
                'sparkline_data': '30,45,60,75,90,98,100',
                'summary': 'Enterprise adoption of multi-agent cognitive architectures for asynchronous workflows.',
                'calculated_score': 96.8,
            },
            {
                'title': 'High-NA EUV Lithography',
                'slug': 'high-na-euv-lithography',
                'category': cat_map['technology'],
                'volume_mentions': 31200,
                'velocity_percentage': 210,
                'sentiment': 'critical',
                'trend_direction': 'up',
                'movement_text': '+8 ranks this week',
                'article_count': 87,
                'is_hot': True,
                'sparkline_data': '40,42,55,68,74,88,94',
                'summary': 'Next-generation semiconductor fabrication reaching sub-2nm node commercialization.',
                'calculated_score': 89.4,
            },
            {
                'title': 'Commercial Fusion Ignition',
                'slug': 'commercial-fusion-ignition',
                'category': cat_map['science'],
                'volume_mentions': 28400,
                'velocity_percentage': 185,
                'sentiment': 'bullish',
                'trend_direction': 'up',
                'movement_text': '+12 ranks this week',
                'article_count': 64,
                'is_hot': True,
                'sparkline_data': '20,30,45,60,70,82,91',
                'summary': 'Record continuous plasma containment milestones unlocking clean data center energy.',
                'calculated_score': 84.1,
            },
            {
                'title': 'Sovereign Digital Reserves',
                'slug': 'sovereign-digital-reserves',
                'category': cat_map['business'],
                'volume_mentions': 22500,
                'velocity_percentage': 145,
                'sentiment': 'volatile',
                'trend_direction': 'up',
                'movement_text': '+5 ranks today',
                'article_count': 53,
                'is_hot': False,
                'sparkline_data': '50,48,62,65,72,78,85',
                'summary': 'Central banks transitioning treasury liquidity to atomic tokenized settlement networks.',
                'calculated_score': 79.5,
            },
            {
                'title': 'Solid-State Battery Scale',
                'slug': 'solid-state-battery-scale',
                'category': cat_map['science'],
                'volume_mentions': 19300,
                'velocity_percentage': 120,
                'sentiment': 'bullish',
                'trend_direction': 'up',
                'movement_text': '+9 ranks this week',
                'article_count': 42,
                'is_hot': False,
                'sparkline_data': '25,35,40,55,62,70,80',
                'summary': 'Automotive manufacturers scaling ceramic electrolyte chemistry for long-range EVs.',
                'calculated_score': 74.0,
            },
            {
                'title': 'Brain-Computer Code Synthesis',
                'slug': 'brain-computer-code-synthesis',
                'category': cat_map['technology'],
                'volume_mentions': 17800,
                'velocity_percentage': 95,
                'sentiment': 'bullish',
                'trend_direction': 'steady',
                'movement_text': 'Holding rank #6',
                'article_count': 38,
                'is_hot': False,
                'sparkline_data': '60,62,65,68,70,72,76',
                'summary': 'Direct cortical neural decoders mapping mental logic to production code.',
                'calculated_score': 71.2,
            },
            {
                'title': 'Quantum Error Correction',
                'slug': 'quantum-error-correction',
                'category': cat_map['technology'],
                'volume_mentions': 25600,
                'velocity_percentage': 170,
                'sentiment': 'critical',
                'trend_direction': 'up',
                'movement_text': '+7 ranks today',
                'article_count': 59,
                'is_hot': True,
                'sparkline_data': '35,45,50,65,75,85,92',
                'summary': 'Logical qubit fault tolerance thresholds achieved in dual superconducting arrays.',
                'calculated_score': 82.3,
            },
            {
                'title': 'Orbital Space Freight',
                'slug': 'orbital-space-freight',
                'category': cat_map['science'],
                'volume_mentions': 14200,
                'velocity_percentage': 88,
                'sentiment': 'neutral',
                'trend_direction': 'steady',
                'movement_text': 'Holding rank #8',
                'article_count': 29,
                'is_hot': False,
                'sparkline_data': '40,42,48,50,55,58,64',
                'summary': 'Commercial reusable upper-stage rockets drastically cutting per-kilogram deployment fees.',
                'calculated_score': 66.8,
            },
        ]

        topic_map = {}
        for tdata in topics_data:
            topic, _ = TrendingTopic.objects.update_or_create(
                slug=tdata['slug'],
                defaults=tdata
            )
            topic_map[tdata['slug']] = topic
        self.stdout.write(self.style.SUCCESS(f"Trending topics synchronized: {len(topic_map)} topics ready."))

        # 4. News Articles
        now = timezone.now()
        articles_data = [
            {
                'title': 'Autonomous Multi-Agent Networks Surpass Human Engineering Velocity in Hardware Simulation',
                'slug': 'autonomous-multi-agent-networks-surpass-human-velocity',
                'category': cat_map['technology'],
                'source': src_map['MIT Technology Review'],
                'source_name': 'MIT Technology Review',
                'source_domain': 'technologyreview.com',
                'author': 'Dr. Alistair Finch',
                'url': 'https://intel.trendora.io/dispatches/autonomous-multi-agent-networks-engineering',
                'image_url': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80',
                'image_gradient': 'linear-gradient(135deg, #1e1b4b 0%, #311042 100%)',
                'hero_pattern': 'neural-grid',
                'published_at': now - timedelta(minutes=18),
                'summary': 'Hierarchical agent swarms autonomously verify complex verilog silicon circuits, demonstrating 14x faster closure on timing bottlenecks.',
                'content': 'A benchmark release from frontier compute teams details a 200-agent cluster cooperating across verification layers to discover edge-case timing violations in 2nm processor layouts. The synthesis protocol uses real-time probabilistic tree search combined with executable formal models to isolate microarchitectural faults that previously required weeks of manual testbench construction.',
                'key_takeaways_json': json.dumps([
                    'Autonomous multi-agent swarms achieve 14x acceleration in silicon circuit timing verification.',
                    'Direct reduction of multi-month chip physical design cycles to under 72 hours.',
                    'Zero hallucinations reported due to formal math verifiers embedded in the loop.'
                ]),
                'read_time_minutes': 5,
                'impact_score': 98,
                'velocity_score': '+340% / 1h',
                'sentiment': 'BULLISH',
                'related_topic': topic_map['autonomous-ai-agents'],
                'is_featured': True,
                'is_breaking': True,
            },
            {
                'title': 'Global Semiconductor Alliance Deploys High-NA EUV Systems to Commercial Fabs',
                'slug': 'global-semiconductor-alliance-deploys-high-na-euv-systems',
                'category': cat_map['technology'],
                'source': src_map['Wired Strategic Dispatch'],
                'source_name': 'Wired Strategic Dispatch',
                'source_domain': 'wired.com',
                'author': 'Marcus Lin, Silicon Analyst',
                'url': 'https://intel.trendora.io/dispatches/semiconductor-high-na-euv-commercial-fabs',
                'image_url': 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80',
                'image_gradient': 'linear-gradient(135deg, #022c22 0%, #064e3b 100%)',
                'hero_pattern': 'circuit-glow',
                'published_at': now - timedelta(minutes=45),
                'summary': 'High numerical aperture extreme ultraviolet photolithography begins volume production, achieving 8-nanometer pitch resolution.',
                'content': 'Commercial wafer foundries have integrated 0.55 NA optics into full manufacturing lines, printing sub-10nm critical feature pitches in single exposure steps. This breakthrough avoids costly multi-patterning steps, expanding chip yields while reducing electrical power requirements for datacenter accelerators.',
                'key_takeaways_json': json.dumps([
                    '0.55 NA systems reduce lithography exposure passes from four to one.',
                    'Yield curves project a 22% manufacturing cost saving per good die.',
                    'Foundry production capacity for 2026-2027 fully reserved by leading AI labs.'
                ]),
                'read_time_minutes': 4,
                'impact_score': 94,
                'velocity_score': '+210% / 1h',
                'sentiment': 'HIGH IMPACT',
                'related_topic': topic_map['high-na-euv-lithography'],
                'is_featured': True,
                'is_breaking': False,
            },
            {
                'title': 'Commercial Tokamak Sustains High-Temperature Fusion Burn for 48 Hours Continuous',
                'slug': 'commercial-tokamak-sustains-high-temperature-fusion-burn',
                'category': cat_map['science'],
                'source': src_map['Nature Quantum Review'],
                'source_name': 'Nature Quantum Review',
                'source_domain': 'nature.com',
                'author': 'Dr. Arthur Pendelton',
                'url': 'https://intel.trendora.io/dispatches/tokamak-high-temperature-fusion-record',
                'image_url': 'https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=1200&q=80',
                'image_gradient': 'linear-gradient(135deg, #172554 0%, #1e1b4b 100%)',
                'hero_pattern': 'quantum-wave',
                'published_at': now - timedelta(hours=1, minutes=30),
                'summary': 'Magnetic confinement trial maintains Q=1.45 power gain, establishing viability for zero-carbon high-density computing campuses.',
                'content': 'Plasma physicists achieved continuous divertor heat exhaust stabilization at over 120 million degrees Celsius without disrupting the boundary layer. Major cloud computing providers have initiated joint ventures to finance commercial grid connections starting late 2027.',
                'key_takeaways_json': json.dumps([
                    'Stable magnetic confinement sustained for 2,880 minutes without disruption.',
                    'Demonstrates continuous Q > 1 energy multiplication in compact magnet geometry.',
                    'Data center operators sign exploratory power-purchase agreements for clean baseload.'
                ]),
                'read_time_minutes': 6,
                'impact_score': 96,
                'velocity_score': '+185% / 1h',
                'sentiment': 'BULLISH',
                'related_topic': topic_map['commercial-fusion-ignition'],
                'is_featured': False,
                'is_breaking': True,
            },
            {
                'title': 'Cross-Border Real-Time Central Bank Atomic Settlement Protocol Enters Production',
                'slug': 'cross-border-central-bank-atomic-settlement-production',
                'category': cat_map['business'],
                'source': src_map['Bloomberg Terminal Wire'],
                'source_name': 'Bloomberg Terminal Wire',
                'source_domain': 'bloomberg.com',
                'author': 'Claire Sterling',
                'url': 'https://intel.trendora.io/dispatches/central-bank-atomic-settlement-protocol',
                'image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80',
                'image_gradient': 'linear-gradient(135deg, #3b0764 0%, #18181b 100%)',
                'hero_pattern': 'cyber-mesh',
                'published_at': now - timedelta(hours=2, minutes=15),
                'summary': 'Multilateral monetary consortium executes atomic foreign exchange clearance in 1.4 seconds, slashing bilateral correspondent risks.',
                'content': 'Sovereign clearing houses have initiated live liquidity swaps across five international currency corridors utilizing cryptographic multi-party authorization. The architecture bypasses correspondent banking delays while offering provable zero-knowledge compliance verification.',
                'key_takeaways_json': json.dumps([
                    'Clearing latency plummeted from T+2 days to 1,400 milliseconds.',
                    'Elimination of Herstatt settlement risk via cryptographic atomic locks.',
                    'Treasury operations save an estimated $42 billion annually in capital reserve drag.'
                ]),
                'read_time_minutes': 4,
                'impact_score': 91,
                'velocity_score': '+145% / 1h',
                'sentiment': 'BULLISH',
                'related_topic': topic_map['sovereign-digital-reserves'],
                'is_featured': False,
                'is_breaking': False,
            },
            {
                'title': 'Automotive Ceramic Solid-State Battery Attains 1,100 KM Range in Highway Cycle',
                'slug': 'automotive-ceramic-solid-state-battery-1100km-range',
                'category': cat_map['science'],
                'source': src_map['The Financial Times'],
                'source_name': 'The Financial Times',
                'source_domain': 'ft.com',
                'author': 'Henrik Larsson',
                'url': 'https://intel.trendora.io/dispatches/automotive-solid-state-battery-breakthrough',
                'image_url': 'https://images.unsplash.com/photo-1558441719-8b489c63f732?auto=format&fit=crop&w=1200&q=80',
                'image_gradient': 'linear-gradient(135deg, #18181b 0%, #1e293b 100%)',
                'hero_pattern': 'neural-grid',
                'published_at': now - timedelta(hours=3, minutes=10),
                'summary': 'Lithium-metal solid electrolyte modules demonstrate 92% capacity retention across 1,500 rapid charge cycles.',
                'content': 'Production-ready battery packs utilizing ceramic separators have completed standardized highway dynamometer testing without degradation. An 8-minute charge delivers 600 kilometers of range while operating safely across temperature extremes from -30C to +60C.',
                'key_takeaways_json': json.dumps([
                    'Volumetric energy density increases to 520 Wh/kg at cell level.',
                    '8-minute ultra-fast recharge replenishes 60% pack state of charge.',
                    'Commercial passenger vehicles equipped with solid electrolyte enter delivery in Q4.'
                ]),
                'read_time_minutes': 4,
                'impact_score': 88,
                'velocity_score': '+120% / 1h',
                'sentiment': 'BULLISH',
                'related_topic': topic_map['solid-state-battery-scale'],
                'is_featured': False,
                'is_breaking': True,
            },
            {
                'title': 'Non-Invasive Cortical Decoder Translates Neural Intent to High-Level Code',
                'slug': 'non-invasive-cortical-decoder-neural-intent-to-code',
                'category': cat_map['technology'],
                'source': src_map['MIT Technology Review'],
                'source_name': 'MIT Technology Review',
                'source_domain': 'technologyreview.com',
                'author': 'Sarah Chen, Neural Interface Lab',
                'url': 'https://intel.trendora.io/dispatches/neural-bci-direct-code-synthesis',
                'image_url': 'https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=1200&q=80',
                'image_gradient': 'linear-gradient(135deg, #2e1065 0%, #0f172a 100%)',
                'hero_pattern': 'matrix-stream',
                'published_at': now - timedelta(hours=4, minutes=50),
                'summary': 'Engineers demonstrate thought-to-syntax interface operating with 96% semantic fidelity without surgical implantation.',
                'content': 'By combining high-density magnetoencephalography with contextual foundation models, participants successfully authored multi-threaded Python algorithms simply by conceptualizing architectural logic. The platform provides transformative capabilities for motor-impaired developers.',
                'key_takeaways_json': json.dumps([
                    '96% semantic translation accuracy for algorithmic abstractions.',
                    'Zero latency feedback loop through auditory synthesized confirmation.',
                    'Open standard protocol proposed for medical and industrial applications.'
                ]),
                'read_time_minutes': 5,
                'impact_score': 92,
                'velocity_score': '+95% / 1h',
                'sentiment': 'BULLISH',
                'related_topic': topic_map['brain-computer-code-synthesis'],
                'is_featured': False,
                'is_breaking': False,
            },
            {
                'title': 'Global AI Sovereign Governance Treaty Signed by 42 Nations in Geneva',
                'slug': 'global-ai-sovereign-governance-treaty-geneva',
                'category': cat_map['politics'],
                'source': src_map['Reuters Intelligence'],
                'source_name': 'Reuters Intelligence',
                'source_domain': 'reuters.com',
                'author': 'Helena Rostova, Diplomatic Bureau',
                'url': 'https://intel.trendora.io/dispatches/global-ai-governance-treaty-geneva',
                'image_url': 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=1200&q=80',
                'image_gradient': 'linear-gradient(135deg, #1e1b4b 0%, #311042 100%)',
                'hero_pattern': 'cyber-mesh',
                'published_at': now - timedelta(hours=5, minutes=40),
                'summary': 'International accord sets binding thresholds for autonomous frontier model safety verifications and critical compute audits.',
                'content': 'Signatories established the International Neural Safety Directorate, an inspection body with authority to review frontier clusters exceeding 10^27 FLOP training limits. The accord balances innovation acceleration with strict containment standards for self-improving agents.',
                'key_takeaways_json': json.dumps([
                    'Binding international framework for compute-intensive model oversight.',
                    'Creation of verified hardware enclave inspection standards.',
                    'Exemption granted for open-source academic research under 10^25 FLOPs.'
                ]),
                'read_time_minutes': 5,
                'impact_score': 89,
                'velocity_score': '+78% / 1h',
                'sentiment': 'DEVELOPING',
                'related_topic': None,
                'is_featured': False,
                'is_breaking': True,
            },
            {
                'title': 'Real-Time Biometric Telemetry Transforms High-Performance Endurance Racing',
                'slug': 'biometric-telemetry-high-performance-endurance-racing',
                'category': cat_map['sports'],
                'source': src_map['The Financial Times'],
                'source_name': 'The Financial Times',
                'source_domain': 'ft.com',
                'author': 'Carlos Mendez',
                'url': 'https://intel.trendora.io/dispatches/biometric-telemetry-endurance-racing',
                'image_url': 'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=1200&q=80',
                'image_gradient': 'linear-gradient(135deg, #172554 0%, #1e1b4b 100%)',
                'hero_pattern': 'circuit-glow',
                'published_at': now - timedelta(hours=7, minutes=20),
                'summary': 'Formula 1 teams integrate millisecond neural feedback gloves to monitor driver cognitive fatigue through telemetry arrays.',
                'content': 'Telemetry systems equipped with galvanic skin response and EEG sensor bands track driver alertness through high-G turns. Team strategists adjust pit stops and aerodynamic modes according to real-time driver cognitive reserve indices.',
                'key_takeaways_json': json.dumps([
                    'Continuous EEG stream transmitted over 5G vehicle-to-pit transceivers.',
                    'Predicts driver reaction degradation 4 laps prior to visible lap time drops.',
                    'Regulatory review planned for standardized implementation across motorsports.'
                ]),
                'read_time_minutes': 4,
                'impact_score': 82,
                'velocity_score': '+64% / 1h',
                'sentiment': 'NEUTRAL',
                'related_topic': None,
                'is_featured': False,
                'is_breaking': False,
            },
            {
                'title': 'Generative Neural Rendering Engines Revolutionize Interactive Cinema Production',
                'slug': 'generative-neural-rendering-interactive-cinema-production',
                'category': cat_map['entertainment'],
                'source': src_map['Wired Strategic Dispatch'],
                'source_name': 'Wired Strategic Dispatch',
                'source_domain': 'wired.com',
                'author': 'Chloe Montgomery',
                'url': 'https://intel.trendora.io/dispatches/generative-neural-rendering-cinema',
                'image_url': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1200&q=80',
                'image_gradient': 'linear-gradient(135deg, #3b0764 0%, #18181b 100%)',
                'hero_pattern': 'matrix-stream',
                'published_at': now - timedelta(hours=8, minutes=15),
                'summary': 'Next-generation volumetric Gaussian splatting creates real-time interactive cinema branching based on viewer biometric reactions.',
                'content': 'Major studio releases premiere interactive features where photographic camera angles and narrative arcs adjust dynamically at 60 fps to viewer engagement. The production workflow replaces traditional post-production rendering with live neural radiance field evaluation.',
                'key_takeaways_json': json.dumps([
                    'Real-time photorealistic volumetric rendering at 60 frames per second.',
                    'Narrative branching tailored to viewer pupillometry and heart rate.',
                    'Significant cost reduction in physical sets and CGI VFX pipelines.'
                ]),
                'read_time_minutes': 4,
                'impact_score': 85,
                'velocity_score': '+55% / 1h',
                'sentiment': 'BULLISH',
                'related_topic': None,
                'is_featured': False,
                'is_breaking': False,
            },
        ]

        article_count = 0
        for adata in articles_data:
            art, _ = NewsArticle.objects.update_or_create(
                url=adata['url'],
                defaults=adata
            )
            article_count += 1
        self.stdout.write(self.style.SUCCESS(f"News articles synchronized: {article_count} baseline articles loaded."))

        # 5. Demo Analyst User Account
        demo_user, created = User.objects.get_or_create(
            username='demo_analyst',
            defaults={
                'email': 'analyst@trendora.intel',
                'first_name': 'Alexander',
                'last_name': 'Vance',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        demo_user.set_password('Trendora2026!')
        demo_user.save()

        # Update profile
        profile, _ = UserProfile.objects.get_or_create(user=demo_user)
        profile.avatar_color = '#8b5cf6'
        profile.bio = 'Chief Intelligence Analyst tracking autonomous agent swarms, macroeconomic shifts, and frontier quantum architectures.'
        profile.preferred_categories.set([cat_map['technology'], cat_map['science'], cat_map['business']])
        profile.save()

        # Bookmark top 2 articles for demo analyst
        first_two = NewsArticle.objects.all()[:2]
        for a in first_two:
            SavedArticle.objects.get_or_create(user=demo_user, article=a)

        self.stdout.write(self.style.SUCCESS(f"Demo analyst account configured: 'demo_analyst' / 'Trendora2026!'."))
        self.stdout.write(self.style.SUCCESS("All baseline intelligence data successfully seeded into TRENDORA!"))
