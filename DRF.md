Các biến mặc định trong View (DRF View/ViewSet)
Khi bạn kế thừa từ APIView, GenericAPIView, hoặc ViewSet, DRF cung cấp cho bạn một số biến mặc định rất hữu ích:
self.request: Đối tượng request hiện tại (giống request trong Django view truyền thống, nhưng đã được DRF mở rộng).
self.response: Không có mặc định, bạn phải trả về Response(...).
self.kwargs: Dictionary chứa các tham số từ URL (ví dụ: pk, slug...).
self.args: Tuple các tham số vị trí từ URL (ít dùng).
self.get_queryset(): Hàm trả về queryset mặc định cho view.
self.get_serializer(): Hàm trả về serializer instance.
self.action: (chỉ có ở ViewSet) – tên action hiện tại (list, retrieve, create, custom action...).
self.request là gì?
self.request là đối tượng request hiện tại, được DRF mở rộng từ Django HttpRequest.
Bạn có thể truy cập:
self.request.user: User đã xác thực (nếu có)
self.request.data: Dữ liệu body (POST, PUT, PATCH)
self.request.query_params: Tham số trên URL (?page=1...)
self.request.method: Phương thức HTTP (GET, POST, ...)
self.request.FILES: File upload
self.request.auth: Thông tin xác thực (token, session...)

Các biến mặc định trong Serializer
Khi bạn kế thừa từ Serializer hoặc ModelSerializer, DRF cung cấp các biến mặc định:
self.instance: Object hiện tại (None nếu tạo mới, object nếu cập nhật)
self.initial_data: Dữ liệu thô từ request
self.validated_data: Dữ liệu đã validate
self.context: Context được truyền vào serializer
self.fields: Dict các field của serializer
self.errors: Dict chứa lỗi validation
self.data: Dữ liệu đã serialize (chỉ có sau khi gọi .data)

1. Các hàm mặc định trong ViewSet/GenericAPIView
   A. Liên quan đến dữ liệu
   get_queryset(self)
   → Trả về queryset cho view.
   get_object(self)
   → Lấy object cụ thể (dùng cho retrieve, update, destroy).
   get_serializer(self, args, kwargs)
   → Trả về instance của serializer (có thể custom context, fields...).
   get_serializer_class(self)
   → Trả về class serializer sẽ dùng (có thể custom theo action).
   B. Liên quan đến quyền và xác thực
   get_permissions(self)
   → Trả về list permission class cho view (có thể custom theo action).
   get_authenticators(self)
   → Trả về list authenticator class cho view.
   C. Liên quan đến filter, pagination
   get_filter_backends(self)
   → Trả về list filter backend.
   get_paginated_response(self, data)
   → Trả về response đã phân trang.
   paginate_queryset(self, queryset)
   → Phân trang queryset.
   D. Liên quan đến action (ViewSet)
   list(self, request, args, kwargs)
   → Xử lý GET list.
   retrieve(self, request, args, kwargs)
   → Xử lý GET detail.
   create(self, request, args, kwargs)
   → Xử lý POST create.
   update(self, request, args, kwargs)
   → Xử lý PUT update.
   partial_update(self, request, args, kwargs)
   → Xử lý PATCH update.
   destroy(self, request, args, kwargs)
   → Xử lý DELETE.
   E. Liên quan đến serializer
   perform_create(self, serializer)
   → Gọi khi tạo object (bạn có thể custom logic trước khi save).
   perform_update(self, serializer)
   → Gọi khi update object.
   perform_destroy(self, instance)
   → Gọi khi xóa object.
2. Một số hàm mặc định trong Serializer
   validate(self, data)
   → Validate cross-field.
   validate\_<fieldname>(self, value)
   → Validate từng trường.
   create(self, validated_data)
   → Tạo object mới.
   update(self, instance, validated_data)
   → Update object.
   to_representation(self, instance)
   → Custom cách serialize object thành dict.
   to_internal_value(self, data)
   → Custom cách deserialize dict thành object.
   is_valid(self, raise_exception=False)
   → Kiểm tra tính hợp lệ của dữ liệu.
   save(self, \*\*kwargs)
   → Lưu object (gọi create hoặc update tùy context).
3. Một số hàm mặc định trong Permission
   has_permission(self, request, view)
   → Kiểm tra quyền ở cấp view.
   has_object_permission(self, request, view, obj)
   → Kiểm tra quyền ở cấp object.
   Tóm lại
   DRF cung cấp rất nhiều hàm mặc định để bạn override và custom logic.
   Quan trọng nhất:
   get_queryset, get_serializer_class, get_permissions, perform_create, perform_update, validate, create, update, ...

Các trường mặc định của class Meta trong Django model
db_table Đặt tên bảng trong database (mặc định là <app_label><model_name>) |
| ordering | Sắp xếp mặc định khi truy vấn (ví dụ: ['-created_at']) |
| unique_together| Đảm bảo kết hợp nhiều trường là duy nhất (tuple hoặc list các tuple) |
| index_together | Tạo index cho nhiều trường cùng lúc (ít dùng, đã deprecated từ Django 2.2) |
| verbose_name | Tên hiển thị cho model (số ít) |
| verbose_name_plural | Tên hiển thị cho model (số nhiều) |
| permissions | Định nghĩa permission custom cho model |
| default_related_name | Tên related_name mặc định cho các quan hệ FK/M2M |
| get_latest_by | Trường mặc định cho truy vấn latest() |
| app_label | Gán model cho app khác (ít dùng) |
| managed | Nếu False, Django sẽ không tự động tạo/migrate bảng này (dùng cho view hoặc bảng ngoài) |
| abstract | Nếu True, model này là abstract base class, không tạo bảng riêng |
| proxy | Nếu True, model này là proxy model (không tạo bảng mới, chỉ thay đổi hành vi) |
| default_permissions | Quyền mặc định tạo ra cho model (add, change, delete, view) |
| indexes | Định nghĩa index nâng cao (từ Django 2.2 trở lên) |
| constraints | Định nghĩa constraint nâng cao (từ Django 2.2 trở lên) |


Trong Django REST Framework (DRF), có một số quy ước đặt tên phương thức trong serializer để tự động liên kết (hook) với các trường nhất định. Dưới đây là các quy ước phổ biến:
1. get_<field_name>(self, obj)
Dùng cho: SerializerMethodField
Chức năng: Tự động gọi hàm này để lấy giá trị cho trường SerializerMethodField.
Ví dụ:
2. validate_<field_name>(self, value)
Dùng cho: Validate từng trường riêng lẻ.
Chức năng: Tự động gọi hàm này để kiểm tra và xử lý giá trị của trường trước khi lưu.
Ví dụ:
3. to_representation(self, instance)
Dùng cho: Tùy biến dữ liệu trả về (output) của serializer.
Chức năng: Ghi đè toàn bộ quá trình chuyển instance thành dict.
4. to_internal_value(self, data)
Dùng cho: Tùy biến quá trình chuyển dữ liệu đầu vào thành object.
5. validate(self, attrs)
Dùng cho: Validate liên trường (cross-field validation).
Chức năng: Kiểm tra logic liên quan đến nhiều trường cùng lúc.
Tổng kết các prefix tự động trong DRF serializers:
Prefix/Hàm	Tác dụng tự động với trường
get_<field_name>	Cho SerializerMethodField
validate_<field_name>	Validate từng trường
validate	Validate nhiều trường cùng lúc
to_representation	Tùy biến dữ liệu trả về
to_internal_value	Tùy biến dữ liệu đầu vào
Lưu ý:
Các prefix này là quy ước của DRF, chỉ cần đặt đúng tên, DRF sẽ tự động gọi khi cần thiết.
Ngoài ra, các hàm như create, update cũng được DRF tự động gọi khi thực hiện thao tác tương ứng.

Cách sử dụng dấu gạch dưới trong truy vấn
a. Truy vấn qua ForeignKey
Giả sử:
Lấy tất cả user thuộc phòng ban tên là "IT":
(department là ForeignKey, name là trường của Department)
b. Truy vấn qua ManyToManyField
Giả sử:
Lấy tất cả user là thành viên của phòng ban có id=1:
(departments là related_name của ManyToManyField)
c. Truy vấn lồng nhiều cấp
Lấy tất cả user thuộc phòng ban có lead là user có id=5:
(departments → lead → id)
d. Truy vấn ngược (related_name)
Nếu bạn có related_name, bạn có thể truy vấn ngược lại:
(members là related_name của ManyToManyField)
3. Một số ví dụ thực tế
Lấy tất cả nhân viên thuộc các phòng ban mà user là lead:
departments là related_name của ManyToManyField members trong Department.
lead_departments là related_name của ManyToManyField lead trong Department.
Lấy tất cả đơn nghỉ phép của nhân viên thuộc các phòng ban mà user là lead:
4. Tóm tắt quy tắc
modelA__fieldB__fieldC=...: Truy vấn từ model hiện tại sang modelA, rồi sang fieldB, rồi sang fieldC.
Dùng related_name để truy vấn ngược.
Dùng .distinct() khi có thể bị trùng kết quả do nhiều mối quan hệ.