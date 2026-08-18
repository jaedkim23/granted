<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/21/26
 * Time: 3:21 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
?>
<script src="<?php echo WEB_PATH?>/assets/nsfproject/tinymce/tinymce.min.js"></script>
<script>
    tinymce.init({
        selector: '#content',
        plugins: 'lists',
        menubar: 'edit insert view format table', // Customizing the menu set
        toolbar: 'undo redo |blocks| bold italic | bullist numlist | alignleft aligncenter alignright | indent outdent',
        license_key: 'gpl'
    });
</script>
<form method="post">
    <?php
   // $logger->displayUserMessage();
    ?>
    <label for="title">Title:</label>
    <input type="text" id="title" name="title" required value="<?php echo $title; ?>"><br>

    <label for="parentid">Parent ID:</label>
    <input type="number" id="parentid" name="parentid" value="<?php echo $parentid; ?>"><br>

    <label for="active">Active:</label>
    <select name="active" id="active">
        <option value="1" <?php if (($active ?? 0) == 1) echo "selected";?>>Yes</option>
        <option value="0" <?php if (($active ?? 0) == 0) echo 'selected';?>>No</option>
    </select><br>

    <label for="secure">Secure:</label>
    <select name="secure" id="secure">
        <option value="0" <?php if (($secure ?? 0) == 0) echo 'selected';?>>No</option>
        <option value="1" <?php if (($secure ?? 0) == 1) echo "selected";?>>Yes</option>
    </select><br>

    <label for="embed">Embed:</label><br>
    <textarea id="embed" name="embed" rows="4" cols="50"><?php echo $embed; ?></textarea><br>

    <label for="content">Content:</label><br>
    <textarea id="content" name="content" rows="10" cols="50"><?php echo $content; ?></textarea><br>

    <label for="is_default">Home page display:</label>
    <select name="is_default" id="is_default">
        <option value="0" <?php if (($is_default ?? 0) == 0) echo 'selected';?>>No</option>
        <option value="1" <?php if (($is_default ?? 0) == 1) echo "selected";?>>Yes</option>
    </select><br>
    <input type="submit" value="<?php echo $button ?? 'Submit'; ?>">
</form>
