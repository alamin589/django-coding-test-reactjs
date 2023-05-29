from django.views import generic
from product.models import *
from product.serializers import *
from rest_framework.response import Response
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import generics, viewsets
from django.db.models import Q
import datetime
import base64
from django.core.files.base import ContentFile

class BaseVariantView(generic.View):
    model = Product
    template_name = 'products/edit.html'
    success_url = '/product/list/'

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
    pass


class ProductListView(generic.TemplateView):
    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        if self.request.GET.get('title') or self.request.GET.get('variant') or self.request.GET.get('price_from') or self.request.GET.get('price_to') or self.request.GET.get('date'):
            title = self.request.GET.get('title')
            variant = self.request.GET.get('variant')
            price_from = self.request.GET.get('price_from')
            price_to = self.request.GET.get('price_to')
            date = self.request.GET.get('date')
            print("title")
            print(title, variant, price_from, price_to, date)
            if price_from and price_to:
                products = Product.objects.filter(
                    title__icontains=title,
                    productvariant__variant_title__icontains=variant,
                    productvariantprice__price__range=[price_from, price_to],
                    created_at__contains=date
                ).distinct()
            elif not price_from and not price_to:
                products = Product.objects.filter(
                    title__icontains=title,
                    productvariant__variant_title__icontains=variant,
                    created_at__contains=date
                ).distinct()
            elif price_from and not price_to:
                products = Product.objects.filter(
                    title__icontains=title,
                    productvariant__variant_title__icontains=variant,
                    productvariantprice__price__gte=price_from,
                    created_at__contains=date
                ).distinct()
            elif not price_from and price_to:
                products = Product.objects.filter(
                    title__icontains=title,
                    productvariant__variant_title__icontains=variant,
                    productvariantprice__price__lte=price_to,
                    created_at__contains=date
                ).distinct()
        else:
            products = Product.objects.all()
        paginator = Paginator(products, 2)
        page = self.request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        if products.object_list and list(products.object_list)[-1]:
            last_page = list(products.object_list)[-1]
            first_page = list(products.object_list)[0]
            first_id = first_page.id
            last_id = last_page.id
        else:
            first_id = 0
            last_id = 0

        variant = Variant.objects.all()
        context['products'] = products
        context['variants'] = variant
        context['page'] = products
        context['count'] = paginator.count
        context['first'] = first_id
        context['last'] = last_id
        return context
    pass

class ProductEditView(BaseVariantView, UpdateView):
    pk_url_kwarg = 'id'

class ProductAPIViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        title = request.data.get('product_name')
        sku = request.data.get('product_sku')
        description = request.data.get('description')
        product_variants = request.data.get('product_variants')
        product_images = request.data.get('product_images')

        print("product_variants", product_variants)
        


        try:
            if title and sku and description and product_variants:
                product = Product.objects.create(
                    title=title,
                    sku=sku,
                    description=description,
                )
                product.save()
                if product_images:
                    try:
                        for image in product_images:
                            format, imgstr = image.split(';base64,') 
                            ext = format.split('/')[-1] 
                            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                            product_image = ProductImage.objects.create(
                                product=product,
                                file_path=data
                            )
                    except Exception as e:
                        print(e)
                        
                print("product_variants1")
                product_variant_temp = []
                for variant in product_variants:
                    print("variant2")
                    print("variant", variant['option'])
                    pk = int(variant['option'])
                    title = variant['tags']


                    variant = Variant.objects.filter(id=pk).first()
                    print("variant", variant)
                    
                    if variant:
                        product_variant = ProductVariant.objects.create(
                            product=product,
                            variant=variant,
                            variant_title=title,
                        )
                        if product_variant:
                            product_variant_temp.append(product_variant)
                    product_variant.save()
                
                print("product_variants3", product_variants)
                if product_variant_temp:
                    print("product_variantsdddd4")
                    for variant in product_variants:
                        product_variant_price = ProductVariantPrice.objects.create(
                            product_variant_one=product_variant_temp[0],
                            product_variant_two=product_variant_temp[1],
                            product_variant_three=product_variant_temp[2],
                            price=float(variant['price']),
                            stock=int(variant['stock']),
                            product=product
                        )
                        product_variant_price.save()
                return Response({
                    'status': 'success',
                    'message': 'Product created successfully',
                    'data': ProductSerializer(product).data
                })

            else:
                return Response({'status': 'error', 'message': 'Please fill all the fields'})
        except Exception as e:
            print(e)
            return Response({
                'status': 'error',
                'message': 'Something went wrong'
            })