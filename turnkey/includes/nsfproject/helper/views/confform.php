<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/29/26
 * Time: 4:54 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
?>
<p>Note: Changes to the configuration won’t be visible until you navigate to a page following the confirmation page.</p>
<form method="post">
<?php
    foreach($ini as $key => $value)
{
    ?>
    <fieldset>
        <legend><?php echo htmlspecialchars($key)?></legend>
        <?php
        if ($key ==='CSS') {
            ?>
            <p>This should be the webpath to where you have placed your CSS override file.  For example, if you have placed your CSS override file in the css directory of this project, you would enter '/nsfproject/assets/nsfproject/css/yourfilename.css'.</p>
            <?php
        }
        foreach($value as $k => $v) {
            if (is_array($v)) {
                // Handle resourceLinks array
                ?>
                <div class="field-group">
                    <label><?php echo htmlspecialchars($k); ?>:</label>
                    <div class="resource-links-container">
                        <?php
                        $resourceLinkCount = 0;
                        foreach($v as $k2 => $v2) {
                            $resourceLinkCount++;
                            ?>
                            <div class="resource-link-item">
                                <label for="resource-link-<?php echo $resourceLinkCount; ?>"><?php echo $resourceLinkCount; ?>:</label>
                                <input type="text" id="resource-link-<?php echo $resourceLinkCount; ?>" name="<?php echo htmlspecialchars($key); ?>[<?php echo htmlspecialchars($k); ?>][]" value="<?php echo htmlspecialchars($v2); ?>" />
                                <button type="button" class="remove-resource-link">Remove</button>
                            </div>
                            <?php
                        }
                        ?>
                        <!-- Template for new resource links -->
                        <div class="resource-link-template" style="display: none;">
                            <label class="resource-link-label"></label>
                            <input type="text" name="<?php echo htmlspecialchars($key); ?>[<?php echo htmlspecialchars($k); ?>][]" value="" />
                            <button type="button" class="remove-resource-link">Remove</button>
                        </div>
                        <button type="button" class="add-resource-link" data-section="<?php echo htmlspecialchars($key); ?>" data-field="<?php echo htmlspecialchars($k); ?>">Add Resource Link</button>
                    </div>
                </div>
                <?php
            } else {
                // Handle regular fields
                ?>
                <div class="field-group">
                    <label for="<?php echo htmlspecialchars($key . '-' . $k); ?>"><?php echo htmlspecialchars($k); ?>:</label>
                    <input type="text" id="<?php echo htmlspecialchars($key . '-' . $k); ?>" name="<?php echo htmlspecialchars($key); ?>[<?php echo htmlspecialchars($k); ?>]" value="<?php echo htmlspecialchars($v); ?>" />
                </div>
                <?php
            }
        }
        ?>
    </fieldset>
<?php
}
?>
    <div class="form-actions">
        <input type="submit" name="submit" value="Save Configuration" />
    </div>
</form>



<script>
document.addEventListener('DOMContentLoaded', function() {
    // Function to add a new resource link
    function addResourceLink(section, field) {
        const template = document.querySelector('.resource-link-template');
        const container = document.querySelector('.resource-links-container');
        const addButton = container.querySelector('.add-resource-link');

        // Clone the template
        const newItem = template.cloneNode(true);
        newItem.style.display = 'flex';
        newItem.classList.remove('resource-link-template');
        newItem.classList.add('resource-link-item');

        // Update the label number
        const items = container.querySelectorAll('.resource-link-item');
        const itemNumber = items.length + 1;
        newItem.querySelector('.resource-link-label').textContent = itemNumber + ':';

        // Insert before the add button
        container.insertBefore(newItem, addButton);

        // Update all item numbers
        updateItemNumbers(container);
    }

    // Function to remove a resource link
    function removeResourceLink(button) {
        const item = button.closest('.resource-link-item');
        const container = item.closest('.resource-links-container');
        item.remove();
        updateItemNumbers(container);
    }

    // Function to update item numbers
    function updateItemNumbers(container) {
        const items = container.querySelectorAll('.resource-link-item');
        items.forEach((item, index) => {
            const label = item.querySelector('.resource-link-label');
            if (label) {
                label.textContent = (index + 1) + ':';
            }
        });
    }

    // Event listeners
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-resource-link')) {
            const section = e.target.getAttribute('data-section');
            const field = e.target.getAttribute('data-field');
            addResourceLink(section, field);
        }

        if (e.target.classList.contains('remove-resource-link')) {
            removeResourceLink(e.target);
        }
    });
});
</script>
