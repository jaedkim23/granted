<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/17/26
 * Time: 4:01 PM
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
        <th scope="col">Email</th>
    <th scope="col">First</th>
    <th scope="col">Last</th>
    <th scope="col">Level</th>
    <th scope="col">Action</th>
</tr>
<?php foreach ($users as $user): ?>
    <tr>
        <td><?php echo $user['email']?></td>
        <td><?php echo $user['first'] ?></td>
        <td><?php echo $user['last']?></td>
        <td><?php echo $user['level'] ?></td>
        <td><a href="<?php echo WEB_PATH;?>/manage/user/edit/<?= $user['id'] ?>">Edit</a>&nbsp;
            <a href="<?php echo WEB_PATH;?>/manage/user/delete/<?= $user['id'] ?>">Delete</a>
        </td>
    </tr>
<?php endforeach; ?>
    </table>
