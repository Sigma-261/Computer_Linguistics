#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S      // указываем корневой нетерминал грамматики

S -> Word<kwtype="places">;

S -> Word<kwtype="persons">; 

        // правило, выделяющее цепочку, состоящую из одного существительного