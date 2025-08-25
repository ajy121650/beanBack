from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import FloorPlan
from cafe.models import Cafe
from .serializers import FloorPlanSerializer, FloorPlanDetectionSerializer, FloorPlanRequestSerializer
from owner.models import Owner
from inference_sdk import InferenceHTTPClient
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
import json, os, tempfile
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import base64


# 배치도 전체 목록 조회 및 생성 API
class FloorPlanListView(APIView):
    @swagger_auto_schema(
        operation_id="배치도 목록 조회",
        operation_description="모든 배치도의 목록을 반환합니다.",
        responses={200: FloorPlanSerializer(many=True)}
    )
    def get(self, request):
        floor_plans = FloorPlan.objects.prefetch_related("chairs", "tables").all()
        serializer = FloorPlanSerializer(floor_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="배치도 생성",
        operation_description="새로운 배치도를 생성합니다.",
        request_body=FloorPlanRequestSerializer,
        responses={201: FloorPlanSerializer, 400: "Bad Request"}
    )
    def post(self, request):
        width = request.data.get("width")
        height = request.data.get("height")
        cafe_id = request.data.get("cafe_id")

        cafe = Cafe.objects.get(id=cafe_id)
        if not cafe:
            return Response({"error": "Cafe not found"}, status=status.HTTP_404_NOT_FOUND)
        floor_plan = FloorPlan.objects.create(
            width=width,
            height=height,
            cafe=cafe
        )

        serializer = FloorPlanSerializer(floor_plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 배치도 개별 상세 조회, 수정, 삭제 API
class FloorPlanDetailView(APIView):
    @swagger_auto_schema(
        operation_id="배치도 상세 조회",
        operation_description="floorplan_id에 해당하는 배치도의 상세 정보를 반환합니다.",
        manual_parameters=[
            openapi.Parameter(
                'floorplan_id',
                openapi.IN_PATH,
                description="도면 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: FloorPlanSerializer, 404: "Not found"}
    )
    def get(self, request, floorplan_id):
        try:
                floor_plan = FloorPlan.objects.get(id=floorplan_id)
        except:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FloorPlanSerializer(floor_plan)
        return Response(serializer.data, status=status.HTTP_200_OK)
                
    @swagger_auto_schema(
        operation_id="배치도 수정",
        operation_description="floorplan_id에 해당하는 배치도를 수정합니다.",
        request_body=FloorPlanRequestSerializer,
        responses={200: FloorPlanSerializer, 404: "Not found"}
    )
    def put(self, request, floorplan_id):
        floorplan = FloorPlan.objects.get(pk=floorplan_id)
        serializer = FloorPlanRequestSerializer(floorplan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_id="배치도 삭제",
        operation_description="floorplan_id에 해당하는 배치도를 삭제합니다.",
        responses={204: "No Content", 404: "Not found"}
    )
    def delete(self, request, floorplan_id):
        try:
            floor_plan = FloorPlan.objects.get(pk=floorplan_id)
            floor_plan.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FloorPlan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


# 점주별 배치도 조회 API
class FloorPlanOwnerView(APIView):
    @swagger_auto_schema(
        operation_id="소유자별 배치도 조회",
        operation_description="owner_id에 해당하는 소유자의 모든 배치도를 반환합니다.",
        manual_parameters=[
            openapi.Parameter(
                'owner_id',
                openapi.IN_PATH,
                description="소유자 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: FloorPlanSerializer(many=True), 404: "Not found"}
    )
    def get(self, request, owner_id):
        try: 
            owner = Owner.objects.get(id=owner_id)
            cafes = Cafe.objects.filter(owner=owner_id)
            cafes_id = cafes.values_list('id', flat=True)
            floor_plans = FloorPlan.objects.filter(cafe__in=cafes_id)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FloorPlanSerializer(floor_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 카페별 배치도 조회 API
class FloorPlanCafeView(APIView):
    @swagger_auto_schema(
        operation_id="카페별 배치도 조회",
        operation_description="cafe_id에 해당하는 카페의 모든 배치도를 반환합니다.",
        manual_parameters=[
            openapi.Parameter(
                'cafe_id',
                openapi.IN_PATH,
                description="카페 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: FloorPlanSerializer(many=True), 404: "Not found"}
    )
    def get(self, request, cafe_id):
        try:
            cafe = Cafe.objects.get(id=cafe_id)
        except Cafe.DoesNotExist:
            return Response({"error": "Cafe not found"}, status=status.HTTP_404_NOT_FOUND)

        floor_plans = FloorPlan.objects.filter(cafe=cafe).prefetch_related("chairs", "tables")
        serializer = FloorPlanSerializer(floor_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 도면 요소 탐지 API 클래스
class FloorPlanDetectionView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_id="도면 요소 탐지",
        operation_description="이미지 URL을 통해 도면에서 요소를 탐지해서 배치도 정보를 생성합니다.",
        manual_parameters=[
            openapi.Parameter(
                'image_url',
                openapi.IN_QUERY,
                description="이미지 URL",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: FloorPlanDetectionSerializer, 400: "Bad Request"}
    )

    def post(self, request):
        image = request.FILES.get('image')
        if not image:
            return Response({"error": "No image uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
            for chunk in image.chunks():
                temp_image.write(chunk)
            temp_image_path = temp_image.name
            
        if not os.path.exists(temp_image_path):
            print(f"Temporary file not found: {temp_image_path}")
            raise FileNotFoundError(f"Temporary file not found: {temp_image_path}")
        
        api_key = os.getenv("ROBOFLOW_API_KEY")
        
        if not api_key:
            return Response(
                {"error": "Server misconfigured: missing ROBOFLOW_API_KEY"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
        client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=api_key,
        )
            
        try:
            with open(temp_image_path, "rb") as image_file:
                print("before run_workflow")
                print("Workspace name:", "cho-voxnn")
                print("Workflow ID:", "detect-count-and-visualize")
                print("Use cache:", False)
                
                # 파일 내용을 Base64로 인코딩
                image_content = base64.b64encode(image_file.read()).decode('utf-8')
                print("Image content size (Base64):", len(image_content), "characters")
                
                # Base64 데이터를 전달
                result = client.run_workflow(
                    workspace_name="cho-voxnn",
                    workflow_id="detect-count-and-visualize-2",
                    images={"image": image_content},
                    use_cache=False
                )
                print("Workflow executed successfully.")
                print("Result:", result)
        except Exception as e:
            print("An error occurred while running the workflow:")
            print(e)
            

        
        
        try:
            print(json.dumps(result, indent=2))

            # result 검증
            if not isinstance(result, list) or len(result) == 0:
                return Response(
                    {"error": "Invalid result format or empty result."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            first = result[0]

            # 필요한 키 검증
            if "predictions" not in first or "image" not in first["predictions"]:
                return Response(
                    {"error": "Missing required keys in result."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            detections = first["predictions"].get("predictions", [])
            image_data = first["predictions"]["image"]

            if "width" not in image_data or "height" not in image_data:
                return Response(
                    {"error": "Missing image dimensions in result."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            width = image_data["width"]
            height = image_data["height"]

            response_data = {
                "image_size": {
                    "width": width,
                    "height": height
                },
                "detections": [
                    {
                        "class": det.get("class", "unknown"),
                        "confidence": det.get("confidence", 0),
                        "x": det.get("x", 0),
                        "y": det.get("y", 0),
                        "width": det.get("width", 0),
                        "height": det.get("height", 0)
                    }
                    for det in detections
                ]
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except KeyError as e:
            return Response(
                {"error": f"KeyError: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except IndexError as e:
            return Response(
                {"error": f"IndexError: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )