import pytest
from django.conf import settings
from django.utils.timezone import now
from tests import assert_num_queries

from pretix.base.models import Event, Organizer
from pretix.multidomain.models import KnownDomain
from pretix.multidomain.urlreverse import build_absolute_uri, eventreverse


@pytest.fixture
def env():
    o = Organizer.objects.create(name='MRMCD', slug='mrmcd')
    event = Event.objects.create(
        organizer=o, name='MRMCD2015', slug='2015',
        date_from=now()
    )
    settings.SITE_URL = 'http://example.com'
    return o, event


@pytest.mark.django_db
def test_event_main_domain_front_page(env):
    assert eventreverse(env[1], 'presale:event.index') == '/mrmcd/2015/'
    assert eventreverse(env[0], 'presale:organizer.index') == '/mrmcd/'


@pytest.mark.django_db
def test_event_custom_domain_kwargs(env):
    KnownDomain.objects.create(domainname='foobar', organizer=env[0])
    assert eventreverse(env[1], 'presale:event.checkout', {'step': 'payment'}) == 'http://foobar/2015/checkout/payment/'


@pytest.mark.django_db
def test_event_main_domain_kwargs(env):
    assert eventreverse(env[1], 'presale:event.checkout', {'step': 'payment'}) == '/mrmcd/2015/checkout/payment/'


@pytest.mark.django_db
def test_event_custom_domain_front_page(env):
    KnownDomain.objects.create(domainname='foobar', organizer=env[0])
    assert eventreverse(env[1], 'presale:event.index') == 'http://foobar/2015/'
    assert eventreverse(env[0], 'presale:organizer.index') == 'http://foobar/'


@pytest.mark.django_db
def test_event_custom_domain_keep_port(env):
    settings.SITE_URL = 'http://example.com:8081'
    KnownDomain.objects.create(domainname='foobar', organizer=env[0])
    assert eventreverse(env[1], 'presale:event.index') == 'http://foobar:8081/2015/'


@pytest.mark.django_db
def test_event_custom_domain_keep_scheme(env):
    settings.SITE_URL = 'https://example.com'
    KnownDomain.objects.create(domainname='foobar', organizer=env[0])
    assert eventreverse(env[1], 'presale:event.index') == 'https://foobar/2015/'


@pytest.mark.django_db
def test_event_main_domain_cache(env):
    env[0].get_cache().clear()
    with assert_num_queries(1):
        eventreverse(env[1], 'presale:event.index')
    with assert_num_queries(0):
        eventreverse(env[1], 'presale:event.index')


@pytest.mark.django_db
def test_event_custom_domain_cache(env):
    KnownDomain.objects.create(domainname='foobar', organizer=env[0])
    env[0].get_cache().clear()
    with assert_num_queries(1):
        eventreverse(env[1], 'presale:event.index')
    with assert_num_queries(0):
        eventreverse(env[1], 'presale:event.index')


@pytest.mark.django_db
def test_event_custom_domain_cache_clear(env):
    kd = KnownDomain.objects.create(domainname='foobar', organizer=env[0])
    env[0].get_cache().clear()
    with assert_num_queries(1):
        eventreverse(env[1], 'presale:event.index')
    kd.delete()
    with assert_num_queries(1):
        eventreverse(env[1], 'presale:event.index')


@pytest.mark.django_db
def test_event_main_domain_absolute(env):
    assert build_absolute_uri(env[1], 'presale:event.index') == 'http://example.com/mrmcd/2015/'


@pytest.mark.django_db
def test_event_custom_domain_absolute(env):
    KnownDomain.objects.create(domainname='foobar', organizer=env[0])
    assert build_absolute_uri(env[1], 'presale:event.index') == 'http://foobar/2015/'
