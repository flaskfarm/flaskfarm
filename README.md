# Changelog
- 4.1.6 (2024.06.06)   
  확장 설정도 메뉴 적용 가능 하도록 수정.   
  확장 설정에서는 uri가 반드시 플러그인을 나타내지 않기 떄문에 순서를 위해서는 plugin을 key로 사용해야 함.   
  예:      
  ```
  - name: "시스템"
  list:
    - uri: "system"
      name: "설정"
    - uri: "setting"
      name: "확장 설정"
      list:
        - uri: "https://drive.google.com"
          name: 구글 드라이브
        - uri: "-"
        - plugin: "flaskcode"
        - plugin: "terminal"
        - plugin: "flaskfilemanager"
        - uri: "-"
        - plugin: "trans"
        - uri: "-"
        - plugin: "support_site"
        - uri: "-"
  ```

- 4.1.4 (2024.06.01)   
  SuppportString.remove_emoji 추가   
