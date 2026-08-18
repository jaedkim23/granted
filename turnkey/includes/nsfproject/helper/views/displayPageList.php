<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/24/26
 * Time: 4:21 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
?>

<table>
    <tr>
        <th scope="col">ID</th>
        <th scope="col">Title</th>
        <th scope="col">Active</th>
        <th scope="col">Require Login</th>
        <th scope="col">Home Page display</th>
        <th scope="col">Parent ID</th>
        <th scope="col">Action</th>
    </tr>
    <?php
    foreach ($pages as $page) {
        ?>
        <tr>
            <td><?php echo $page['id']?></td>
            <td><?php echo $page['title'];?></td>
            <td><?php echo ($page['active']===1?'Yes':'No');?></td>
            <td><?php echo $page['secure']===1?'Yes':'No';?></td>
            <td><?php echo $page['is_default']===1?'Yes':'No';?></td>
            <td><?php echo $page['parentid']??'none'?></td>
            <td><a href="<?php echo WEB_PATH; ?>/manage/pages/edit/<?php echo $page['id'];?>">Edit</a></td>
        </tr>
    <?php
    }
    ?>
</table>