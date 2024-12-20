**Transaction Weekly and Monthly Charts**


**Monthly Chart**


There are two approaches to calculating the monthly transaction chart based on the Jalali calendar:

1. Using a Complex Query with a Conversion Function:<br>
   This method involves using a function to convert Gregorian dates to Jalali and grouping transactions by Jalali year and month. Below is the MongoDB query for calculating the Jalali `createdAt`:

```
[
  {
    $addFields: {
      gy: { $year: "$createdAt" },
      gm: { $month: "$createdAt" },
      gd: { $dayOfMonth: "$createdAt" }
    }
  },
  {
    $project: {
      gm: true,
      gd: true,
      gy: {
        $subtract: [
          "$gy",
          { $cond: { if: { $lte: ["$gy", 1600] }, then: 621, else: 1600 } }
        ]
      },
      g_d_m: [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334],
      jy: { $cond: { if: { $lte: ["$gy", 1600] }, then: 0, else: 979 } }
    }
  },
  {
    $project: {
      gy: true,
      gm: true,
      gd: true,
      jy: true,
      g_d_m: true,
      gy2: {
        $cond: { if: { $gt: ["$gm", 2] }, then: { $add: ["$gy", 1] }, else: "$gy" }
      }
    }
  },
  {
    $project: {
      gy2: true,
      gy: true,
      gm: true,
      gd: true,
      jy: true,
      g_d_m: true,
      days: {
        $add: [
          { $multiply: [365, "$gy"] },
          { $toInt: { $divide: [{ $add: ["$gy2", 3] }, 4] } },
          { $toInt: { $divide: [{ $add: ["$gy2", 399] }, 400] } },
          "$gd",
          { $arrayElemAt: ["$g_d_m", { $subtract: ["$gm", 1] }] },
          { $multiply: [-1, { $add: [80, { $toInt: { $divide: [{ $add: ["$gy2", 99] }, 100] } }] }] }
        ]
      }
    }
  },
  {
    $project: {
      gy2: true,
      gy: true,
      gm: true,
      gd: true,
      g_d_m: true,
      jy: {
        $add: [
          "$jy",
          { $multiply: [33, { $toInt: { $divide: ["$days", 12053] } }] }
        ]
      },
      days: { $mod: ["$days", 12053] }
    }
  },
  {
    $project: {
      gy2: true,
      gy: true,
      gm: true,
      gd: true,
      g_d_m: true,
      jy: {
        $add: [
          "$jy",
          { $multiply: [4, { $toInt: { $divide: ["$days", 1461] } }] }
        ]
      },
      days: { $mod: ["$days", 1461] }
    }
  },
  {
    $project: {
      gy2: true,
      gy: true,
      gm: true,
      gd: true,
      gdm: true,
      jy: {
        $add: [
          "$jy",
          { $toInt: { $divide: [{ $subtract: ["$days", 1] }, 365] } }
        ]
      },
      days: {
        $cond: {
          if: { $gt: ["$days", 365] },
          then: { $mod: [{ $subtract: ["$days", 1] }, 365] },
          else: "$days"
        }
      }
    }
  },
  {
    $project: {
      jy: true,
      jm: {
        $cond: {
          if: { $lt: ["$days", 186] },
          then: { $add: [1, { $toInt: { $divide: ["$days", 31] } }] },
          else: { $add: [7, { $toInt: { $divide: [{ $subtract: ["$days", 186] }, 30] }] }] }
        }
      },
      jd: {
        $add: [
          1,
          {
            $cond: {
              if: { $lt: ["$days", 186] },
              then: { $mod: ["$days", 31] },
              else: { $mod: [{ $subtract: ["$days", 186] }, 30] }
            }
          }
        ]
      }
    }
  },
  {
    $project: {
      jy: { $toInt: "$jy" },
      jm: { $toInt: "$jm" },
      jd: { $toInt: "$jd" }
    }
  }
]
```

2. Grouping by Day and Aggregating at the Application Level:<br>
   This method groups data by day using MongoDB queries, and the aggregation by Jalali month is done at the application level. This solution has been implemented.


**Weekly Chart**

For calculating the weekly transaction chart based on the Jalali calendar, there are three approaches:

1. Add One Day to the `createdAt` Field: <br>
   By adding one day to each transaction's `createdAt` field (treating Saturdays as Sundays), the transactions can be grouped by week using MongoDB. This solution returns the Gregorian week of the year number. However, this approach **does not meet the requirements of the task**, as it does not directly calculate the Jalali week.

2. Calculate Jalali Dates and Day of Year, Then Divide by 7: <br>
   This method calculates the Jalali day of the year, then divides it by 7 to get weekly groupings. This solution assumes each year starts on a Saturday, but **it does not align with the task's specifications**, as the weeks are not correctly adjusted for the actual Jalali calendar.

3. Grouping by Day and Aggregating at the Application Level: <br>
   Similar to the monthly chart, this approach groups the data by day in MongoDB and then aggregates by Jalali month at the application level. This solution has been implemented and meets the task's requirements.
