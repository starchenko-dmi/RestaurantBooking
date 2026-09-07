from .models import FooterDocument, HeroImage, SocialLink


def footer_data(request):
    """
    Добавляет данные для футера во все шаблоны:
    - social_links: активные соцсети
    - footer_documents: активные документы
    - hero_image: изображение баннера
    """
    return {
        "social_links": SocialLink.objects.filter(is_active=True).order_by("order")[:5],
        "footer_documents": FooterDocument.objects.filter(is_active=True)[:5],
        "hero_image": HeroImage.objects.first(),
    }
