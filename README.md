# Changelog
- 4.1.14 (2024.06.19)   
  * main.py 에서 CELERYD_HIJACK_ROOT_LOGGER=false export(set)   
  * 로그 UI 변경.
  * framework, plugin 전체 로그를 all.log 에 기록.   
  * ModelBase에 get_list_by_status 메소드 추가.   

- 4.1.14 (2024.06.12)   
  `import flaskfarm` 만으로 전체기능 로딩되지 않게 수정.   

- 4.1.11 (2024.06.11)   
  DB 전체(기간) 삭제시 VACUUM 수행.   

- 4.1.7 (2024.06.05)   
  확장 설정에서 하위 페이지(setting_menu 에서 list)를 처리할 수 있도록 수정.   

- 4.1.6 (2024.06.04)   
  확장 설정도 menu.yaml 적용 가능 하도록 수정.   
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
