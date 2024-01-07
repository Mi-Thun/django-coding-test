from django.views import generic

from django.views import View
from django.shortcuts import render
from product.models import Product, ProductVariant, ProductVariantPrice, Variant
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Subquery, OuterRef

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
    items_per_page = 5

    def get_context_data(self, **kwargs):
        title_query = self.request.GET.get('title', '')
        date_query = self.request.GET.get('date', '')
        price_from = self.request.GET.get('price_from', '')
        price_to = self.request.GET.get('price_to', '')
        variant_s = self.request.GET.get('variant', '')

        context = {'products': Product.objects.all()}
        if title_query:
            context['products'] = context['products'].filter(title__icontains=title_query)

        if date_query:
            context['products'] = context['products'].filter(created_at__date=date_query)

        if price_from and price_to:
            filtered_prices = ProductVariantPrice.objects.filter(price__gte=price_from, price__lte=price_to)
        else:
            filtered_prices = ProductVariantPrice.objects.all()

        variant_ids = [variant_id for variant_id in filtered_prices.values_list('product_variant_one', 'product_variant_two', 'product_variant_three', 'product') if variant_id is not None]
        for product in context['products']:
            if variant_s:
                product.variants = ProductVariant.objects.filter(product=product, variant_title=variant_s, variant__in=variant_ids) if variant_ids else []
            else:
                product.variants = ProductVariant.objects.filter(product=product, variant__in=variant_ids) if variant_ids else []
            for variant in product.variants:
                variant.prices = ProductVariantPrice.objects.filter(product=product)
                
        context['products'] = [product for product in context['products'] if getattr(product, 'variants', None)]


        if price_from and price_to:
            filtered_product_ids = [
                product.id for product in context['products'] if
                ProductVariantPrice.objects.filter(
                    product=product,
                    price__gte=price_from,
                    price__lte=price_to
                ).exists()
            ]
            context['products'] = [product for product in context['products'] if product.id in filtered_product_ids]

        paginator = Paginator(context['products'], self.items_per_page)
        page = self.request.GET.get('page')

        try:
            context['products'] = paginator.page(page)
        except PageNotAnInteger:
            context['products'] = paginator.page(1)
        except EmptyPage:
            context['products'] = paginator.page(paginator.num_pages)
            
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['variants'] = list(variants.all())

        productvariants = ProductVariant.objects.filter().values('id', 'variant', 'product', 'variant_title')
        context['productvariants'] = list(productvariants.all())

        context['variant_data'] = [
            {
                'variant': variant,
                'productvariants': [
                    pv for pv in context['productvariants'] if pv['variant'] == variant['id']
                ]
            }
            for variant in context['variants']
        ]
        
        unique_titles = set()
        filtered_data = [
            {
                'variant': variant,
                'productvariants': [
                    pv for pv in productvariants if pv['variant_title'] not in unique_titles and (unique_titles.add(pv['variant_title']) or True)
                ]
            }
            for variant, productvariants in [(item['variant'], item['productvariants']) for item in context['variant_data']]
        ]
        context['variant_data'] = filtered_data
        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)





