select assert_equals('dummyplug.txt',fs('./fixture/fs/')); 

select assert_equals('dummyplug.txt',fs('./fixture', "*/*")); 

select assert_equals('dummyplug.txt',fs('./fixture', "*/*.txt")); 

.exit