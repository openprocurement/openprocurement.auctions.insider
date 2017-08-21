��                �      �  E   �  �   3  �        �  K  �  K         Y  =   z     �  !   �  h   �     O  �   X  �   =  i   *  
   �  P   �     �  D   �     >	  I   M	  v   �	  !   
  ~   0
  �   �
  9   ;  G   u  Y   �      w     O  �  �   �     �  @  �  �     :   �  �   �     `  =   y  �   �       �  �  |    �   �     j  �   �  
   #  \   .     �  Z   �  �   �  9   �  �       �  O   �  G     �   f   *Auction.value* is gradually decreasing per 1% during the Dutch part. API accepts `JSON <http://json.org/>`_ or form-encoded content in requests.  It returns JSON content in all of its responses, including errors.  Only the UTF-8 character encoding is supported for both requests and responses. API is relatively stable. The changes in the API are communicated via `Open Procurement API <https://groups.google.com/group/open-procurement-api>`_ maillist. API stability All API POST and PUT requests expect a top-level object with a single element in it named `data`.  Successful responses will mirror this format. The data element should itself be an object, containing the parameters for the request.  In the case of creating a new auction, these are the fields we want to set on the auction itself. Auction consists of 3 stages: Dutch auction, sealed bid and best bid parts. Auction is passing within a day. Bidders can enter the auction till the end of the Dutch part. Conventions Documentation of related packages During *active.tendering* period participants can ask questions, submit proposals, and upload documents. Features If something went wrong during the request, we'll get a different status code and the JSON returned will have an `errors` field at the top level containing a list of problems.  We look at the first one and print out its message. If the request was successful, we will get a response code of `201` indicating the object was created.  That response will have a data field at its top level, which will contain complete information on the new auction, including its ID. In case of no bid has been made within Dutch auction, the whole procedure will be marked as unsuccessful. Next steps Organizer can't edit procedure's significant properties (*Auction.value*, etc.). Overview Procedure can be switched from *draft* status to *active.tendering*. Project status The only currency (*Value.currency*) for this procedure is hryvnia (UAH). The only date Organizer has to provide is *Tender.auctionPeriod.startDate*, the rest will be calculated automatically. The project has pre alpha status. The source repository for this project is on GitHub: `<https://github.com/openprocurement/openprocurement.auctions.insider>`_. There is obligatory participant qualification (*Bid.selfQualified*) via guarantee payment. It has to be paid till 16:00 of the auction day. You might find it helpful to look at the :ref:`tutorial`. `OpenProcurement API <http://api-docs.openprocurement.org/en/latest/>`_ openprocurement.auctions.dutch contains documentaion for Deposit Guarantee Fund auctions. Project-Id-Version: openprocurement.auctions.dgf 0.1
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2016-09-12 15:36+0300
PO-Revision-Date: 2016-10-20 17:33+0200
Last-Translator: Zoriana Zaiats <sorenabell@quintagroup.com>
Language-Team: Ukrainian <support@quintagroup.com>
Language: uk
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
X-Generator: Lokalize 2.0
 *Auction.value* поступово знижується на 1% протягом Голландського етапу. API приймає `JSON <http://json.org/>`_ або form-encoded вміст у запитах. Він повертає JSON вміст у всіх свої відповідях, включно з помилками. Підтримується лише UTF-8 кодування і для запитів, і для відповідей. API є відносно стабільним. Зміни в API обговорюються через `Open Procurement API <https://groups.google.com/group/open-procurement-api>`_ розсилку. Стабільність API Всі API POST та PUT запити очікують об'єкт верхнього рівня з єдиним елементом з назвою `data`. Відповіді з повідомленням про успіх будуть віддзеркалювати цей формат. Елемент data повинен сам бути об’єктом, що містить параметри запиту. Якщо створюється новий аукціон, то це ті поля, які ми хочемо встановити на самому аукціоні. Аукціон проводиться у три етапи: Голландський аукціон, sealed bid та best bid частини. Аукціон проходить упродовж дня. Учасники можуть долучатися до аукціону аж до завершення Голландського етапу. Домовленості Документація пов’язаних пакетів Протягом періоду *active.tendering* учасники можуть задавати питання, подавати пропозиції, завантажувати документи. Особливості Якщо під час запиту виникли труднощі, ми отримаємо інший код стану та JSON, який при поверненні міститиме `errors` поле на верхньому рівні зі списком проблем. Ми дивимось на першу з них і видруковуємо її повідомлення. Якщо запит був успішним, ми отримаємо код відповіді `201`, який вказує, що об’єкт був створений. Ця відповідь буде мати data поле на верхньому рівні, яке вміщуватиме повну інформацію про новий аукціон, включно з ID. Якщо жоден учкасник не зробить цінової пропозиції під час Голландського аукціону, процедура вважається неуспішною. Наступні кроки Організатор не може редагувати суттєвих властивостей процедури, наприклад, *Auction.value*. Огляд Процедура переходить зі статусу *draft* до *active.tendering*. Стан проекту Єдина валюта (*Value.currency*) цієї процедури - гривня UAH. Єдина дата, яку потрібно надати, це дата початку аукціону *Tender.auctionPeriod.startDate*. Всі решта дати будуть обраховані на її основі. Статус цього проекту пре-альфа. Репозиторій джерельних текстів цього проекту є на GitHub `<https://github.com/openprocurement/openprocurement.auctions.insider>`_. Обов’язкова кваліфікація учасника (*Bid.selfQualified*) через гарантійний платіж. Гарантійний внесок має бути сплачений до 16:00 дня проведення аукціону. Можливо вам буде цікаво прочитати :ref:`tutorial`. `OpenProcurement API <http://api-docs.openprocurement.org/en/latest/>`_ openprocurement.auctions.dutch містить документацію по аукціонах Фонду гарантування вкладів. 