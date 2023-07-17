import unittest
from datetime import date, datetime
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactModel
from src.repository.contacts import get_contacts, get_contact_by_id, create, get_contact_by_email, update, remove, \
    find_contact_by_firstname, find_contact_by_lastname, find_contacts_birthday


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query(Contact).limit().offset().all.return_value = contacts
        result = await get_contacts(10, 0, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id_found(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_id(contact_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_id_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_contact_by_id(contact_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_get_contact_by_email_found(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_email(email='test@meta.ua', db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_email_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_contact_by_email(email='test@meta.ua', db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(
            first_name='Ivan',
            last_name='Ivanenko',
            email='ivanivanenko@meta.ua',
            phone='+380123456789',
            birthday=date(2000, 8, 12)
        )
        result = await create(body, self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)

    async def test_update_contact_found(self):
        body = ContactModel(
            first_name='Ivan',
            last_name='Ivanenko',
            email='ivanivanenko@meta.ua',
            phone='+380123456789',
            birthday=date(2000, 8, 12)
        )
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        self.session.commit.return_value = None
        result = await update(contact_id=1, body=body, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactModel(
            first_name='Ivan',
            last_name='Ivanenko',
            email='ivanivanenko@meta.ua',
            phone='+380123456789',
            birthday=date(2000, 8, 12)
        )
        self.session.query().filter_by().first.return_value = None
        self.session.commit.return_value = None
        result = await update(contact_id=1, body=body, db=self.session)
        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await remove(contact_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await remove(contact_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_find_contact_by_firstname(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter_by().all.return_value = contacts
        result = await find_contact_by_firstname(contact_firstname='Ivan', db=self.session)
        self.assertEqual(result, contacts)

    async def test_find_contact_by_lastname(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter_by().all.return_value = contacts
        result = await find_contact_by_lastname(contact_lastname='Ivanenko', db=self.session)
        self.assertEqual(result, contacts)

    async def test_find_contacts_birthday(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await find_contacts_birthday(db=self.session)
        self.assertEqual(result, contacts)
