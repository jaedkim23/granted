<?php

require_once 'includes/nsfproject/vendor/autoload.php';

$markdown = '[University of San Diego](https://www.sandiego.edu/)';

$parsedown = new Parsedown();

$html = $parsedown->line($markdown);

echo "Original Markdown: $markdown\n";
echo "Parsed HTML: $html\n";
