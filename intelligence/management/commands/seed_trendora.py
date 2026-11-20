from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json
from intelligence.models import Category, TrendingTopic, NewsArticle, UserProfile

class Command(BaseCommand):
    help = 'Seeds complete real-time news, trending topics, categories and demo profile for TRENDORA'

    def handle(self, *args, **options):
        self.stdout.write("Initializing TRENDORA multi-domain intelligence database...")

        # Clear existing items
        NewsArticle.objects.all().delete()
        TrendingTopic.objects.all().delete()
        Category.objects.all().delete()

        # 1. Categories
        categories_data = [
            {
                'name': 'Technology',
                'slug': 'technology',
                'icon': 'cpu',
                'color_code': '#8b5cf6', # Electric Purple
                'badge_class': 'badge-purple',
                'description': 'Frontier artificial intelligence, autonomous agent swarms, neuromorphic chips, and quantum systems.',
                'order': 1
            },
            {
                'name': 'Business',
                'slug': 'business',
                'icon': 'brief',
                'color_code': '#10b981', # Emerald
                'badge_class': 'badge-green',
                'description': 'Global financial markets, venture capital flows, sovereign wealth allocations, and macroeconomics.',
                'order': 2
            },
            {
                'name': 'Politics',
                'slug': 'politics',
                'icon': 'globe',
                'color_code': '#f43f5e', # Rose Red
                'badge_class': 'badge-pink',
                'description': 'Geopolitical diplomacy, international trade accords, semiconductor sovereignty, and defense directives.',
                'order': 3
            },
            {
                'name': 'Sports',
                'slug': 'sports',
                'icon': 'trophy',
                'color_code': '#f59e0b', # Radiant Amber
                'badge_class': 'badge-amber',
                'description': 'Biometric analytics, high-performance athletic engineering, global championships, and sports franchise investments.',
                'order': 4
            },
            {
                'name': 'Science',
                'slug': 'science',
                'icon': 'orbit',
                'color_code': '#06b6d4', # Cyan
                'badge_class': 'badge-cyan',
                'description': 'Commercial tokamak fusion, CRISPR genomic therapeutics, deep-space astrophysics, and material science.',
                'order': 5
            },
            {
                'name': 'Entertainment',
                'slug': 'entertainment',
                'icon': 'film',
                'color_code': '#ec4899', # Magenta/Pink
                'badge_class': 'badge-pink',
                'description': 'Generative cinema, virtual acoustics, interactive gaming engines, and cultural media trends.',
                'order': 6
            },
        ]

        category_objs = {}
        for c in categories_data:
            cat = Category.objects.create(**c)
            category_objs[cat.slug] = cat
        self.stdout.write(f"Created {len(category_objs)} primary intelligence categories.")

        # 2. Trending Topics across all 6 domains
        now = timezone.now()
        trending_data = [
            # Technology
            {
                'title': 'Autonomous Agent Swarms',
                'slug': 'autonomous-agent-swarms',
                'category': category_objs['technology'],
                'volume_mentions': 312000,
                'velocity_percentage': 520,
                'sentiment': 'bullish',
                'trend_direction': 'hot',
                'movement_text': '▲ #1 Global Trend (+520%)',
                'article_count': 64,
                'is_hot': True,
                'sparkline_data': '25,38,44,52,68,82,96',
                'summary': 'Rapid enterprise migration toward decentralized multi-agent coordination pipelines and self-healing software.',
            },
            {
                'title': 'Silicon-Photonics Interconnects',
                'slug': 'silicon-photonics-interconnects',
                'category': category_objs['technology'],
                'volume_mentions': 195000,
                'velocity_percentage': 340,
                'sentiment': 'bullish',
                'trend_direction': 'up',
                'movement_text': '▲ Up 4 spots this week',
                'article_count': 41,
                'is_hot': True,
                'sparkline_data': '30,35,48,59,71,85,92',
                'summary': 'Sub-picojoule optical I/O packaging accelerating hyperscaler token generation cluster throughput.',
            },
            # Business
            {
                'title': 'Sovereign AI GPU Capital Funds',
                'slug': 'sovereign-ai-gpu-funds',
                'category': category_objs['business'],
                'volume_mentions': 188400,
                'velocity_percentage': 295,
                'sentiment': 'bullish',
                'trend_direction': 'up',
                'movement_text': '▲ +295% capital influx',
                'article_count': 38,
                'is_hot': True,
                'sparkline_data': '20,28,45,55,62,78,89',
                'summary': 'National wealth funds pooling $120B+ to secure dedicated nuclear-backed clean compute clusters.',
            },
            {
                'title': 'Decentralized Treasury Reserves',
                'slug': 'decentralized-treasury-reserves',
                'category': category_objs['business'],
                'volume_mentions': 142100,
                'velocity_percentage': 190,
                'sentiment': 'volatile',
                'trend_direction': 'up',
                'movement_text': '▲ High Volatility (+190%)',
                'article_count': 29,
                'is_hot': False,
                'sparkline_data': '40,32,55,48,65,70,82',
                'summary': 'Multinational corporations diversify balance sheets with cryptographic sovereign bond tokenization.',
            },
            # Politics
            {
                'title': 'EU AI Act Enforcement Wave',
                'slug': 'eu-ai-act-enforcement',
                'category': category_objs['politics'],
                'volume_mentions': 165800,
                'velocity_percentage': 310,
                'sentiment': 'critical',
                'trend_direction': 'hot',
                'movement_text': '▲ Mandatory compliance phase',
                'article_count': 47,
                'is_hot': True,
                'sparkline_data': '45,50,42,60,78,85,94',
                'summary': 'Global model providers adjust weights and telemetry protocols to satisfy cross-border audit mandates.',
            },
            {
                'title': 'Critical Rare-Earth Trade Accords',
                'slug': 'rare-earth-trade-accords',
                'category': category_objs['politics'],
                'volume_mentions': 118000,
                'velocity_percentage': 175,
                'sentiment': 'neutral',
                'trend_direction': 'steady',
                'movement_text': '● Diplomatic rounds active',
                'article_count': 23,
                'is_hot': False,
                'sparkline_data': '35,40,42,48,50,55,60',
                'summary': 'Trilateral agreements guarantee supply lines for neodymium, dysprosium, and semiconductor minerals.',
            },
            # Sports
            {
                'title': 'Biometric Neuro-Tracking in Formula 1',
                'slug': 'biometric-neuro-tracking-f1',
                'category': category_objs['sports'],
                'volume_mentions': 134200,
                'velocity_percentage': 260,
                'sentiment': 'bullish',
                'trend_direction': 'up',
                'movement_text': '▲ +260% engagement surge',
                'article_count': 31,
                'is_hot': False,
                'sparkline_data': '18,25,38,49,60,74,86',
                'summary': 'Sub-second cognitive reaction sensors integrated into driver telemetry systems for live race optimization.',
            },
            {
                'title': 'Synthetic Bio-Recovery Protocols',
                'slug': 'synthetic-bio-recovery-sports',
                'category': category_objs['sports'],
                'volume_mentions': 92400,
                'velocity_percentage': 165,
                'sentiment': 'bullish',
                'trend_direction': 'up',
                'movement_text': '▲ Elite athletics adoption',
                'article_count': 19,
                'is_hot': False,
                'sparkline_data': '22,28,34,42,50,62,71',
                'summary': 'Hyperbaric cellular regeneration and targeted peptide recovery reduce soft-tissue rehabilitation cycles by 40%.',
            },
            # Science
            {
                'title': 'Commercial Tokamak 22-Tesla Field',
                'slug': 'commercial-tokamak-fusion-22t',
                'category': category_objs['science'],
                'volume_mentions': 178500,
                'velocity_percentage': 380,
                'sentiment': 'bullish',
                'trend_direction': 'hot',
                'movement_text': '▲ Record confinement test',
                'article_count': 52,
                'is_hot': True,
                'sparkline_data': '15,22,35,48,62,79,93',
                'summary': 'Superconducting REBCO magnet arrays sustain record high-pressure plasma confinement for 72 hours.',
            },
            {
                'title': 'Non-Abelian Majorana Qubit Braiding',
                'slug': 'majorana-qubit-braiding',
                'category': category_objs['science'],
                'volume_mentions': 125000,
                'velocity_percentage': 240,
                'sentiment': 'bullish',
                'trend_direction': 'up',
                'movement_text': '▲ Fault-tolerant milestone',
                'article_count': 35,
                'is_hot': False,
                'sparkline_data': '20,32,40,52,65,73,88',
                'summary': 'Topological immunity reduces physical-to-logical quantum error overhead from 10,000:1 to under 20:1.',
            },
            # Entertainment
            {
                'title': 'Real-Time Neural World-Building Engines',
                'slug': 'neural-world-building-engines',
                'category': category_objs['entertainment'],
                'volume_mentions': 156300,
                'velocity_percentage': 325,
                'sentiment': 'bullish',
                'trend_direction': 'up',
                'movement_text': '▲ AAA Studios integration',
                'article_count': 44,
                'is_hot': True,
                'sparkline_data': '25,34,46,60,72,84,95',
                'summary': 'Diffusion-driven 3D game engines generate volumetric photorealistic environments interactively at 120 FPS.',
            },
            {
                'title': 'Binaural Spatial Acoustics Synthesis',
                'slug': 'binaural-spatial-acoustics',
                'category': category_objs['entertainment'],
                'volume_mentions': 88600,
                'velocity_percentage': 155,
                'sentiment': 'bullish',
                'trend_direction': 'steady',
                'movement_text': '● Streaming platform rollout',
                'article_count': 22,
                'is_hot': False,
                'sparkline_data': '30,35,38,44,52,60,68',
                'summary': 'Ray-traced personal acoustic rendering delivers cinema-grade spatial immersion through standard earbuds.',
            },
        ]

        topic_objs = {}
        for t in trending_data:
            topic = TrendingTopic.objects.create(**t)
            topic_objs[topic.slug] = topic
        self.stdout.write(f"Created {len(topic_objs)} cross-domain trending topics.")

        # 3. Rich News Articles across all 6 categories
        articles_data = [
            # TECHNOLOGY (Featured)
            {
                'title': 'Next-Gen Neuromorphic AI Processors Achieve 100x Energy Efficiency Milestone in Real-Time Sensor Processing',
                'slug': 'neuromorphic-ai-processors-100x-energy-efficiency',
                'category': category_objs['technology'],
                'source_name': 'MIT Technology Review',
                'source_domain': 'technologyreview.com',
                'source_badge_color': '#8b5cf6',
                'published_at': now - timedelta(minutes=14),
                'summary': 'Monolithic 3D neuromorphic silicon architecture processes continuous multi-modal sensory streams with under 15 milliwatts of total thermal dissipation.',
                'content': '''A landmark publication released today by an international consortium of university laboratories and semiconductor fabricators details a working 3D neuromorphic core that mimics mammalian cortical sparse-coding. Operating on event-driven asynchronous spikes rather than clock-synchronous tensor matrix arithmetic, the processor demonstrated an astonishing 100-fold reduction in energy draw during live robotic spatial navigation and acoustic signal filtering tasks.

The breakthrough relies on atomic-layer-deposited memristive crossbar arrays directly bonded onto sub-2nm FinFET logic layers. Unlike conventional GPUs and specialized transformer accelerators that consume hundreds of watts during continuous token generation, neuromorphic cores only expend power when an informative delta or "spike" registers across synaptic nodes.

"We are witnessing the convergence of biological compute principles with commercial silicon manufacturing," remarked Dr. Elena Vance, lead investigator at the Cambridge Neuro-Silicon Institute. "This eliminates the memory wall and thermal bottlenecks that have throttled real-time autonomous systems operating in extreme edge environments."''',
                'key_takeaways_json': json.dumps([
                    '100x reduction in watt-per-operation envelope relative to leading 3nm GPU architectures.',
                    'Zero static leakage power achieved via event-driven asynchronous spike-timing logic.',
                    'Direct 3D bonding of memristor arrays eliminates the classical von Neumann memory wall.',
                    'Commercial tape-out agreements targeted for Q3 2027 across industrial foundry consortia.'
                ]),
                'read_time_minutes': 5,
                'impact_score': 98,
                'velocity_score': '+540% / 1h',
                'sentiment': 'BULLISH',
                'image_gradient': 'linear-gradient(135deg, #1e1b4b 0%, #3b0764 100%)',
                'hero_pattern': 'neural-grid',
                'related_topic': topic_objs['autonomous-agent-swarms'],
                'is_featured': True,
                'is_breaking': True,
                'views_count': 8420,
                'bookmarks_count': 612,
            },
            # BUSINESS
            {
                'title': 'Sovereign Wealth Funds Commit $120B to Autonomous Clean Compute Infrastructure Parks',
                'slug': 'sovereign-wealth-funds-commit-120b-clean-compute',
                'category': category_objs['business'],
                'source_name': 'Financial Times',
                'source_domain': 'ft.com',
                'source_badge_color': '#10b981',
                'published_at': now - timedelta(minutes=42),
                'summary': 'State-backed investment vehicles across Gulf and ASEAN coalitions secure gigawatt-scale nuclear and solar co-location pacts for sovereign AI data centers.',
                'content': '''Sovereign wealth funds across the Middle East and Southeast Asian economies have finalized dedicated multi-decade financing pipelines exceeding $120 billion. In an effort to secure digital sovereignty and shield critical infrastructure from global cloud supply shocks, the entities are building gigawatt-scale data center campuses wired directly into sovereign nuclear and solar microgrids.

The strategy represents a structural pivot from passive venture capital allocations into physical energy and computing infrastructure ownership, establishing national AI foundation models as sovereign public utilities.''',
                'key_takeaways_json': json.dumps([
                    '$120B+ combined capital deployment allocated across 2026-2030 fiscal pipelines.',
                    'Direct co-location with dedicated clean energy microgrids (SMR nuclear & high-density solar).',
                    'Sovereign foundation models to be treated as critical public utility infrastructure.'
                ]),
                'read_time_minutes': 4,
                'impact_score': 94,
                'velocity_score': '+390% / 1h',
                'sentiment': 'BULLISH',
                'image_gradient': 'linear-gradient(135deg, #022c22 0%, #065f46 100%)',
                'hero_pattern': 'market-bull',
                'related_topic': topic_objs['sovereign-ai-gpu-funds'],
                'is_featured': False,
                'is_breaking': True,
                'views_count': 6150,
                'bookmarks_count': 420,
            },
            # POLITICS
            {
                'title': 'Global AI Treaty Ratified by 42 Nations Establishing Algorithmic Non-Proliferation Standards',
                'slug': 'global-ai-treaty-ratified-42-nations',
                'category': category_objs['politics'],
                'source_name': 'Reuters Global Policy',
                'source_domain': 'reuters.com',
                'source_badge_color': '#f43f5e',
                'published_at': now - timedelta(hours=1, minutes=15),
                'summary': 'International delegates conclude historic Geneva convention, instituting mandatory verifiable watermarks and inspection regimes for autonomous cyber-weapons.',
                'content': '''Diplomats representing 42 leading industrial and emerging economies have signed the Geneva Accord on Autonomous Systems. The landmark treaty mandates cryptographic verification for all frontier foundation models with training compute budgets exceeding 10^26 FLOPs.

Under the framework, member states agree to prohibit fully autonomous offensive cyber-reconnaissance and create an international inspection registry modeled after the International Atomic Energy Agency (IAEA).''',
                'key_takeaways_json': json.dumps([
                    '42 signatory nations enact harmonized verification protocols for frontier compute models.',
                    'Creation of the International Algorithmic Safety Commission (IASC) with spot-inspection powers.',
                    'Strict prohibition on fully autonomous offensive cyber capabilities targeting civilian utilities.'
                ]),
                'read_time_minutes': 5,
                'impact_score': 96,
                'velocity_score': '+460% / 1h',
                'sentiment': 'HIGH IMPACT',
                'image_gradient': 'linear-gradient(135deg, #2b0718 0%, #881337 100%)',
                'hero_pattern': 'shield-mesh',
                'related_topic': topic_objs['eu-ai-act-enforcement'],
                'is_featured': False,
                'is_breaking': True,
                'views_count': 7290,
                'bookmarks_count': 510,
            },
            # SCIENCE
            {
                'title': 'Commercial Tokamak Fusion Reactor Maintains 22-Tesla Steady Plasma Confinement for 72 Hours',
                'slug': 'commercial-tokamak-fusion-22-tesla-record',
                'category': category_objs['science'],
                'source_name': 'Nature Physics',
                'source_domain': 'nature.com',
                'source_badge_color': '#06b6d4',
                'published_at': now - timedelta(hours=2, minutes=10),
                'summary': 'High-temperature rare-earth barium copper oxide (REBCO) superconducting magnet arrays demonstrate stable confinement without quench incidents.',
                'content': '''Fusion energy startup engineers have shattered the magnetic confinement duration record for compact commercial reactors. Utilizing advanced REBCO superconducting tapes, the pilot magnetic coil maintained an intense 22-Tesla magnetic flux density without thermal quench or structural degradation.

Because plasma pressure in a magnetic bottle scales with the fourth power of the magnetic field (B^4), doubling the field strength produces a sixteen-fold increase in fusion power density. This achievement clears the thermodynamic runway for sub-gigawatt commercial power plants with a physical footprint no larger than a standard warehouse.''',
                'key_takeaways_json': json.dumps([
                    'Stable 22-Tesla field sustained continuously over 72 hours under full cryogenic operation.',
                    'B^4 scaling law yields a 16x amplification in plasma power density compared to 11T designs.',
                    'Target net-electricity pilot plant grid demonstration scheduled for 2029.'
                ]),
                'read_time_minutes': 6,
                'impact_score': 95,
                'velocity_score': '+380% / 1h',
                'sentiment': 'BULLISH',
                'image_gradient': 'linear-gradient(135deg, #083344 0%, #0e7490 100%)',
                'hero_pattern': 'plasma-ring',
                'related_topic': topic_objs['commercial-tokamak-fusion-22t'],
                'is_featured': False,
                'is_breaking': False,
                'views_count': 5980,
                'bookmarks_count': 415,
            },
            # SPORTS
            {
                'title': 'Formula 1 Teams Deploy Real-Time Driver Neuro-Telemetry for Sub-Millisecond Cornering Decisions',
                'slug': 'formula-1-neuro-telemetry-cornering',
                'category': category_objs['sports'],
                'source_name': 'Motorsport Tech Journal',
                'source_domain': 'motorsport.com',
                'source_badge_color': '#f59e0b',
                'published_at': now - timedelta(hours=3, minutes=5),
                'summary': 'Helmet-integrated near-infrared spectroscopy sensors correlate cognitive load with aerodynamic downforce adjustments in real time.',
                'content': '''Grand Prix engineering paddocks have introduced live cerebral blood oxygenation monitoring. Fitted non-invasively inside custom carbon-fiber racing helmets, the sensors read micro-delays in driver cognitive recognition under 5G sustained lateral loads.

Machine learning models predict tire degradation and driver fatigue up to 8 laps in advance, informing pit-stop strategy with millimeter precision.''',
                'key_takeaways_json': json.dumps([
                    'Helmet-integrated NIRS sensors track prefrontal cortex oxygenation at 250 Hz.',
                    'Fatigue and reaction decay predicted 8 laps before mechanical lap-time degradation.',
                    'Approved by FIA for integration into standard telemetry broadcast streams.'
                ]),
                'read_time_minutes': 4,
                'impact_score': 88,
                'velocity_score': '+270% / 1h',
                'sentiment': 'BULLISH',
                'image_gradient': 'linear-gradient(135deg, #241400 0%, #78350f 100%)',
                'hero_pattern': 'speed-vectors',
                'related_topic': topic_objs['biometric-neuro-tracking-f1'],
                'is_featured': False,
                'is_breaking': False,
                'views_count': 4200,
                'bookmarks_count': 230,
            },
            # ENTERTAINMENT
            {
                'title': 'Interactive Neural World-Generation Engines Enable Infinite Real-Time 3D Cinematics',
                'slug': 'interactive-neural-world-generation-engines',
                'category': category_objs['entertainment'],
                'source_name': 'Wired Arts & Media',
                'source_domain': 'wired.com',
                'source_badge_color': '#ec4899',
                'published_at': now - timedelta(hours=3, minutes=45),
                'summary': 'Next-generation video games and virtual cinema abandon pre-rendered polygons in favor of continuous generative diffusion radiance fields.',
                'content': '''Major digital visual effects studios have showcased the first fully responsive virtual cinema experience running at 120 frames per second in 8K resolution. Instead of traditional polygonal vertex meshes and texture maps, the world is synthesized continuously from high-dimensional neural radiance fields (NeRFs).

Every camera angle, character lighting reflection, and atmospheric particle reacts dynamically to viewer vocal cues and biometric attention tracking, blurring the distinction between filmmaking and interactive gaming.''',
                'key_takeaways_json': json.dumps([
                    'Complete elimination of polygon asset baking via real-time neural volumetric synthesis.',
                    '120 FPS frame latency maintained at sub-8ms render thresholds on consumer hardware.',
                    'Pioneering new format of audience-participatory algorithmic storytelling.'
                ]),
                'read_time_minutes': 5,
                'impact_score': 91,
                'velocity_score': '+310% / 1h',
                'sentiment': 'BULLISH',
                'image_gradient': 'linear-gradient(135deg, #35082d 0%, #701a75 100%)',
                'hero_pattern': 'cinema-lens',
                'related_topic': topic_objs['neural-world-building-engines'],
                'is_featured': False,
                'is_breaking': False,
                'views_count': 4890,
                'bookmarks_count': 345,
            },
            # TECHNOLOGY - Additional
            {
                'title': 'Silicon-Photonics Interconnects Enter Mass Production, Sashing Hyperscaler Optical Latency by 70%',
                'slug': 'silicon-photonics-interconnects-mass-production',
                'category': category_objs['technology'],
                'source_name': 'Bloomberg Technology',
                'source_domain': 'bloomberg.com',
                'source_badge_color': '#8b5cf6',
                'published_at': now - timedelta(hours=4, minutes=30),
                'summary': 'Foundry yields for monolithic electro-optical transceivers cross 88%, unlocking terabit-per-second inter-chassis links without copper attenuation.',
                'content': '''Semiconductor packaging giants have announced volume delivery of co-packaged optics (CPO). By routing photons directly onto the compute substrate via microscopic silicon waveguides, data centers overcome the physical reach and thermal limits of electrical copper traces.

Early datacenter deployments reveal a 70% decrease in inter-node communication latency, removing communication bottlenecks that previously crippled distributed trillion-parameter model training.''',
                'key_takeaways_json': json.dumps([
                    'Co-packaged optics yield reaches 88% commercial qualification threshold.',
                    '70% reduction in cluster latency across 64,000-accelerator fabric pods.',
                    'Power consumption slashed from 12 picojoules/bit down to 1.8 picojoules/bit.'
                ]),
                'read_time_minutes': 4,
                'impact_score': 93,
                'velocity_score': '+340% / 1h',
                'sentiment': 'BULLISH',
                'image_gradient': 'linear-gradient(135deg, #1e1b4b 0%, #2e1065 100%)',
                'hero_pattern': 'chip-mesh',
                'related_topic': topic_objs['silicon-photonics-interconnects'],
                'is_featured': False,
                'is_breaking': False,
                'views_count': 5230,
                'bookmarks_count': 380,
            },
            # SCIENCE - Additional
            {
                'title': 'Topological Qubit Majorana Nanowire Braiding Demonstrates Hardware-Level Quantum Fault Immunity',
                'slug': 'topological-qubit-majorana-nanowire-braiding',
                'category': category_objs['science'],
                'source_name': 'MIT Technology Review',
                'source_domain': 'technologyreview.com',
                'source_badge_color': '#06b6d4',
                'published_at': now - timedelta(hours=5, minutes=15),
                'summary': 'Physicists verify non-Abelian statistics in hybrid semiconductor-superconductor junctions, slashing error-correction overhead by 95%.',
                'content': '''In a breakthrough hailed as the "transistor moment" for quantum computing, experimentalists have confirmed stable non-local storage of quantum information. By encoding states into topological braiding of Majorana zero modes, qubits are naturally impervious to thermal vibrations and local electromagnetic noise.

This leap reduces the physical-to-logical qubit ratio from 10,000 physical qubits per logical bit to just 18, accelerating timelines for practical fault-tolerant molecular simulation.''',
                'key_takeaways_json': json.dumps([
                    'Direct experimental validation of topological Majorana braiding signatures.',
                    'Quantum error-correction overhead reduced from 10,000:1 to under 20:1.',
                    'Enables room-size quantum supercomputers capable of solving complex drug discovery equations.'
                ]),
                'read_time_minutes': 5,
                'impact_score': 97,
                'velocity_score': '+480% / 1h',
                'sentiment': 'BULLISH',
                'image_gradient': 'linear-gradient(135deg, #0f172a 0%, #0369a1 100%)',
                'hero_pattern': 'quantum-lattice',
                'related_topic': topic_objs['majorana-qubit-braiding'],
                'is_featured': False,
                'is_breaking': True,
                'views_count': 7400,
                'bookmarks_count': 590,
            }
        ]

        created_articles = []
        for a in articles_data:
            art = NewsArticle.objects.create(**a)
            created_articles.append(art)
        self.stdout.write(f"Created {len(created_articles)} rich multi-domain intelligence articles.")

        # 4. Create Demo User and Profile
        demo_user, created = User.objects.get_or_create(
            username='demo_analyst',
            defaults={
                'email': 'analyst@trendora.io',
                'first_name': 'Sarah',
                'last_name': 'Vance',
                'is_staff': True,
            }
        )
        if created:
            demo_user.set_password('Trendora2026!')
            demo_user.save()
            self.stdout.write("Created demo user: demo_analyst (password: Trendora2026!)")

        # Set up profile with preferred categories and saved articles
        profile = demo_user.profile
        profile.preferred_categories.set([category_objs['technology'], category_objs['business'], category_objs['science']])
        profile.saved_articles.set(created_articles[:4])
        profile.reading_history.set(created_articles[:6])
        profile.save()

        self.stdout.write(self.style.SUCCESS("TRENDORA Intelligence Database successfully refreshed and seeded!"))
