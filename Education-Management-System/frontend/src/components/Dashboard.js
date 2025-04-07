import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Grid, Paper, Typography, Card, CardContent } from '@material-ui/core';
import axios from 'axios';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    padding: theme.spacing(3),
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  card: {
    minWidth: 275,
    margin: theme.spacing(2),
  },
}));

function Dashboard() {
  const classes = useStyles();
  const [stats, setStats] = useState({
    totalCourses: 0,
    totalUsers: 0,
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [coursesRes, usersRes] = await Promise.all([
          axios.get('http://localhost:5000/api/courses'),
          axios.get('http://localhost:5000/api/users')
        ]);
        setStats({
          totalCourses: coursesRes.data.length,
          totalUsers: usersRes.data.length,
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className={classes.root}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6}>
          <Card className={classes.card}>
            <CardContent>
              <Typography variant="h5" component="h2">
                Total Courses
              </Typography>
              <Typography variant="h3">
                {stats.totalCourses}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Card className={classes.card}>
            <CardContent>
              <Typography variant="h5" component="h2">
                Total Users
              </Typography>
              <Typography variant="h3">
                {stats.totalUsers}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </div>
  );
}

export default Dashboard; 