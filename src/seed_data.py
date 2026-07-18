import asyncio
from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.appointment import ServiceType, AstrologerProfile, AstrologerAvailability
from app.models.course import Category, Course, CourseSection, Lecture

async def seed():
    async with AsyncSessionLocal() as db:
        # Create a mock astrologer user
        astrologer_user = User(
            email="expert@astrology.com",
            password_hash=get_password_hash("password123"),
            name="Dr. Jyotish",
            role="instructor"
        )
        db.add(astrologer_user)
        await db.commit()
        await db.refresh(astrologer_user)

        # Create Profile
        profile = AstrologerProfile(
            user_id=astrologer_user.id,
            bio="Renowned Vedic Astrologer with over 20 years of experience in reading stars.",
            experience_years=20,
            price_per_session=50.0,
            rating_avg=4.9,
            is_available=True
        )
        db.add(profile)

        # Create Services
        services = [
            ServiceType(name="Birth Chart Reading", description="Detailed analysis of Janam Kundli", duration_minutes=60, base_price=50.0),
            ServiceType(name="Marriage Compatibility", description="Kundli Matching for prospective couples", duration_minutes=45, base_price=40.0),
            ServiceType(name="Career Consultation", description="Guidance on professional growth", duration_minutes=30, base_price=30.0)
        ]
        db.add_all(services)
        
        # Create Availability for tomorrow
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        
        slots = [
            AstrologerAvailability(astrologer_id=astrologer_user.id, specific_date=tomorrow, start_time=time(10, 0), end_time=time(11, 0)),
            AstrologerAvailability(astrologer_id=astrologer_user.id, specific_date=tomorrow, start_time=time(14, 0), end_time=time(15, 0)),
            AstrologerAvailability(astrologer_id=astrologer_user.id, specific_date=tomorrow, start_time=time(16, 0), end_time=time(17, 0))
        ]
        db.add_all(slots)
        
        # Add Course Categories
        cat_vedic = Category(name="Vedic Astrology", icon="star")
        cat_tarot = Category(name="Tarot Reading", icon="cards")
        db.add_all([cat_vedic, cat_tarot])
        await db.commit()
        await db.refresh(cat_vedic)
        await db.refresh(cat_tarot)

        # Add Course 1: Free Course
        course1 = Course(
            title="Vedic Astrology Fundamentals",
            subtitle="Learn the basics of houses, planets, and signs.",
            description="A comprehensive introduction to Vedic Astrology. Perfect for beginners who want to understand how to read a basic birth chart, the significance of the 12 houses, and the 9 planetary bodies.",
            thumbnail_url="https://images.unsplash.com/photo-1532012197267-da84d127e765?q=80&w=600&auto=format&fit=crop",
            price=0.0, # FREE COURSE
            discount_price=0.0,
            instructor_id=astrologer_user.id,
            category_id=cat_vedic.id,
            level="beginner",
            rating_avg=4.8,
            total_students=1240,
            total_duration_minutes=120,
            is_published=True
        )
        
        # Add Course 2: Paid Course
        course2 = Course(
            title="Tarot Card Reading Masterclass",
            subtitle="Become a professional Tarot reader.",
            description="Dive deep into the symbolism of the Rider-Waite deck. This masterclass covers the Major and Minor Arcana, various spreads, and how to conduct professional readings for clients.",
            thumbnail_url="https://images.unsplash.com/photo-1574868991734-f8503eeebfa4?q=80&w=600&auto=format&fit=crop",
            price=99.99,
            discount_price=49.99,
            instructor_id=astrologer_user.id,
            category_id=cat_tarot.id,
            level="intermediate",
            rating_avg=4.9,
            total_students=856,
            total_duration_minutes=240,
            is_published=True
        )
        
        db.add_all([course1, course2])
        await db.commit()
        await db.refresh(course1)
        await db.refresh(course2)

        # Add Sections and Lectures for Course 1
        c1_s1 = CourseSection(course_id=course1.id, title="Module 1: Introduction", order_index=1)
        c1_s2 = CourseSection(course_id=course1.id, title="Module 2: The 12 Houses", order_index=2)
        db.add_all([c1_s1, c1_s2])
        await db.commit()
        await db.refresh(c1_s1)
        await db.refresh(c1_s2)
        
        dummy_vid = "https://media.w3.org/2010/05/sintel/trailer.mp4"

        lectures = [
            Lecture(section_id=c1_s1.id, title="Welcome to Vedic Astrology", video_url=dummy_vid, duration_seconds=300, order_index=1, is_preview=True),
            Lecture(section_id=c1_s1.id, title="History and Origins", video_url=dummy_vid, duration_seconds=600, order_index=2, is_preview=False),
            Lecture(section_id=c1_s2.id, title="Houses 1 to 4", video_url=dummy_vid, duration_seconds=900, order_index=1, is_preview=False),
            Lecture(section_id=c1_s2.id, title="Houses 5 to 8", video_url=dummy_vid, duration_seconds=900, order_index=2, is_preview=False),
        ]
        db.add_all(lectures)
        
        # Add Sections and Lectures for Course 2
        c2_s1 = CourseSection(course_id=course2.id, title="The Major Arcana", order_index=1)
        db.add(c2_s1)
        await db.commit()
        await db.refresh(c2_s1)
        
        c2_lectures = [
            Lecture(section_id=c2_s1.id, title="The Fool's Journey", video_url=dummy_vid, duration_seconds=1200, order_index=1, is_preview=True),
            Lecture(section_id=c2_s1.id, title="The Magician and High Priestess", video_url=dummy_vid, duration_seconds=1500, order_index=2, is_preview=False),
        ]
        db.add_all(c2_lectures)
        
        await db.commit()
        print("Database seeded with comprehensive mock data successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
