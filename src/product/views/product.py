from django.views import generic

from django.views import View
from django.shortcuts import render
from product.models import Product, ProductVariant, ProductVariantPrice, Variant
from django.db.models import Q

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context

class ProductListView(View):
    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = {'products': Product.objects.all()}
        for product in context['products']:
            product.variants = ProductVariant.objects.filter(product=product)
            for variant in product.variants:
                variant.prices = ProductVariantPrice.objects.filter(
                    Q(product_variant_one_id=variant.id) |
                    Q(product_variant_two_id=variant.id) |
                    Q(product_variant_three_id=variant.id),
                    product=product
                )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)





