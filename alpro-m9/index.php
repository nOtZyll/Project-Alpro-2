<?php
session_start();

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] == 'POST') {

    // Capture data from the form
    $data = [
        $_POST['id'],
        $_POST['fname'],
        $_POST['lname'],
        $_POST['email'],
        $_POST['email2'],
        $_POST['profesi']
    ];

    // Append to the CSV file
    $file = fopen("DataPribadi.csv", "a");
    if ($file) {
        fputcsv($file, $data);
        fclose($file);
        // Debugging: Confirm the data was appended
        echo "Data appended successfully.";
    } else {
        echo "Error: Unable to open the CSV file.";
        exit();
    }

    // Redirect to clear POST data and avoid re-submission
    header("Location: " . $_SERVER['PHP_SELF']);
    exit();
}

// Read CSV Data
$dataArray = [];
$headerRowSkipped = false;

if (($file = fopen("DataPribadi.csv", "r")) !== FALSE) {
    while (($row = fgetcsv($file)) !== FALSE) {
        // Skip the header row from the CSV if not already skipped
        if (!$headerRowSkipped) {
            $headerRowSkipped = true;
            continue;
        }
        $dataArray[] = $row;
    }
    fclose($file);
}

// Handle search and pagination variables
$itemsPerPage = isset($_POST['itemsPerPage']) ? (int)$_POST['itemsPerPage'] : 5;
$searchTerm = isset($_POST['search']) ? $_POST['search'] : '';
$filteredData = array_filter($dataArray, function ($row) use ($searchTerm) {
    return stripos(implode(' ', $row), $searchTerm) !== false;
});

// Pagination for filtered data
$totalItems = count($filteredData);
$totalPages = ceil($totalItems / $itemsPerPage);

// Get current page
$currentPage = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$currentPage = max(1, min($totalPages, $currentPage)); // Ensure current page is valid

// Calculate starting index for pagination
$startIndex = ($currentPage - 1) * $itemsPerPage;

// Sorting Logic
$sortField = isset($_GET['sort']) ? $_GET['sort'] : 'id';
usort($filteredData, function ($a, $b) use ($sortField) {
    $index = array_search($sortField, ['id', 'fname', 'lname', 'email', 'email2', 'profesi']);
    
    // Convert IDs to integers for numerical sorting
    if ($sortField === 'id') {
        return intval($a[$index]) - intval($b[$index]);
    }

    return strcmp($a[$index], $b[$index]);
});

// Paginate remaining filtered data
$paginatedData = array_slice($filteredData, $startIndex, $itemsPerPage);

// Display info for pagination
$showStart = $startIndex + 1;
$showEnd = min($startIndex + $itemsPerPage, $totalItems);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Form</title>
    <link rel="stylesheet" href="styles.css">
    <script>
        function searchFunction() {
            document.getElementById("searchForm").submit();
        }

        function clearSearch() {
            document.getElementById("searchInput").value = '';
            document.getElementById("searchForm").submit();
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>Form Pengisian Data Pribadi</h1>

        <div class="card">
            <form action="index.php" method="POST">
                <label for="id">ID:</label>
                <input type="text" name="id" required placeholder="Enter ID">

                <label for="fname">First Name:</label>
                <input type="text" name="fname" required placeholder="Enter First Name">

                <label for="lname">Last Name:</label>
                <input type="text" name="lname" required placeholder="Enter Last Name">

                <label for="email">Email:</label>
                <input type="email" name="email" required placeholder="Enter Email">

                <label for="email2">Secondary Email:</label>
                <input type="email" name="email2" placeholder="Enter Secondary Email">

                <label for="profesi">Profession:</label>
                <input type="text" name="profesi" required placeholder="Enter Profession">

                <input type="submit" value="Submit">
            </form>
        </div>

        <h2>Daftar Data</h2>
        <form id="searchForm" method="POST">
            <input type="text" id="searchInput" name="search" placeholder="Search..." value="<?= htmlspecialchars($searchTerm) ?>">
            <button type="button" onclick="searchFunction()">Search</button>
            <button type="button" onclick="clearSearch()">Clear</button>
            <select name="itemsPerPage" onchange="this.form.submit()">
                <option value="5" <?= $itemsPerPage == 5 ? 'selected' : '' ?>>5</option>
                <option value="10" <?= $itemsPerPage == 10 ? 'selected' : '' ?>>10</option>
                <option value="25" <?= $itemsPerPage == 25 ? 'selected' : '' ?>>25</option>
                <option value="50" <?= $itemsPerPage == 50 ? 'selected' : '' ?>>50</option>
            </select>
        </form>

        <table>
            <thead>
                <tr>
                    <th><a href="?sort=id&page=<?= $currentPage ?>", style="color:white";>Id</a></th>
                    <th><a href="?sort=fname&page=<?= $currentPage ?>", style="color:white";>F_Name</a></th>
                    <th><a href="?sort=lname&page=<?= $currentPage ?>", style="color:white";>L_Name</a></th>
                    <th><a href="?sort=email&page=<?= $currentPage ?>", style="color:white";>Email</a></th>
                    <th><a href="?sort=email2&page=<?= $currentPage ?>", style="color:white";>Email2</a></th>
                    <th><a href="?sort=profesi&page=<?= $currentPage ?>", style="color:white";>Profesi</a></th>
                </tr>
            </thead>
            <tbody>
            <?php
            foreach ($paginatedData as $row) {
                echo "<tr>";
                foreach ($row as $cell) {
                    echo "<td>" . htmlspecialchars($cell) . "</td>";
                }
                echo "</tr>";
            }
            ?>
            </tbody>
        </table>
        <div class="pagination">
            <span>Showing <?= $showStart ?> to <?= $showEnd ?> of <?= $totalItems ?> entries</span>
            <div>
                <a href="?page=<?= max(1, $currentPage - 1) ?>">Previous</a>

                <?php
                // Show first page
                if ($currentPage > 3) {
                    echo '<a href="?page=1">1</a>'; // Always show first page
                    echo '<span>...</span>'; // Add ellipsis
                }
            
                // Calculate the range of page numbers to display
                $start = max(2, $currentPage - 1);
                $end = min($totalPages - 1, $currentPage + 1);
            
                for ($i = $start; $i <= $end; $i++) {
                    if ($i == $currentPage) {
                        echo '<a href="?page=' . $i . '" class="active">' . $i . '</a>'; // Active page
                    } else {
                        echo '<a href="?page=' . $i . '">' . $i . '</a>'; // Other pages
                    }
                }
            
                // Show last page
                if ($currentPage < $totalPages - 2) {
                    echo '<span>...</span>'; // Add ellipsis
                    echo '<a href="?page=' . $totalPages . '">' . $totalPages . '</a>'; // Always show last page
                }
            
                ?>
                <a href="?page=<?= min($totalPages, $currentPage + 1) ?>">Next</a>
            </div>
        </div>
    </div>
</body>
</html>