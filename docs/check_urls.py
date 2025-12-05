"""
Check all URL patterns in the portal system
Run: python manage.py shell < check_urls.py
"""

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

def list_urls(urlpatterns, prefix=''):
    """Recursively list all URL patterns"""
    urls = []
    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            url_path = prefix + str(pattern.pattern)
            url_name = pattern.name if pattern.name else 'NO NAME'
            urls.append((url_path, url_name))
        elif isinstance(pattern, URLResolver):
            new_prefix = prefix + str(pattern.pattern)
            urls.extend(list_urls(pattern.url_patterns, new_prefix))
    return urls

# Get all URLs
resolver = get_resolver()
all_urls = list_urls(resolver.url_patterns)

# Filter portal URLs
portal_urls = [url for url in all_urls if 'portal' in url[1]]
management_urls = [url for url in all_urls if url[1] in ['admin_home', 'manage_contracts', 'employee_list', 'department_page', 'request_leave']]

print("=" * 100)
print("🔍 PORTAL SYSTEM URLs")
print("=" * 100)

print("\n📋 PORTAL URLs (Employee Self-Service):")
print("-" * 100)
for path, name in sorted(portal_urls, key=lambda x: x[1]):
    print(f"  {name:40s} | /{path}")

print("\n📋 MANAGEMENT URLs (Backward Compatibility):")
print("-" * 100)
for path, name in sorted(management_urls, key=lambda x: x[1]):
    print(f"  {name:40s} | /{path}")

print("\n📊 SUMMARY:")
print("-" * 100)
print(f"  Portal URLs:     {len(portal_urls)}")
print(f"  Management URLs: {len(management_urls)}")
print(f"  Total:          {len(portal_urls) + len(management_urls)}")
print("=" * 100)
